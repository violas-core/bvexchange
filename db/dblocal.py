#!/usr/bin/python3
'''
vlibra libra exchange vtoken db
'''
import operator
import sys,os
sys.path.append(os.getcwd())
sys.path.append("..")
import log
import log.logger
import traceback
import datetime
import sqlalchemy
import stmanage
import random
import comm
from comm.error import error
from comm.result import result
from comm.result import parse_except
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime, UniqueConstraint, Index, String

from baseobject import baseobject
from enum import Enum

#module name
name="dblocal"

class dblocal(baseobject):
    __base = declarative_base()
    __engine = ""
    __session = ""
    __engine = ""

    def __init__(self, name, dbfile, create = True, path = "./datas/localdbs"):
        baseobject.__init__(self, name)
        self.__init_db(dbfile, create, path)

    def __del__(self):
        self.__uninit_db()

    #btc exchange vtoken state
    #state change case:  
    #->FAILED
    #->SUCCEED
    ##SUCCEED->VSUCCEED->COMPLETE
    ##SUCCEED->VFAILED->VSUCCEED->COMPLETE
    ##FAILED->SUCCEED->VSUCCEED->COMPLETE
    ##FAILED->SUCCEED->VFAILED->SUCCEED->COMPLETE
    class state(Enum):
        START       = 0     #no use
        FAILED      = 1     #execute before swap failed, this time can re-execute 
        EFAILED     = 2     #get out amount failed
        ESUCCEED    = 3
        QBFAILED    = 4     #get <to_token_id> blance(swap end) with localdb version, calc diff balance 
        QBSUCCEED   = 5
        FILLFAILED  = 6     #fill map sender failed
        FILLSUCCEED = 7
        PFAILED     = 8     #payment(libra token) failed
        PSUCCEED    = 9     #payment(libra token) succeed
        VFAILED     = 10    #send change state transaction failed
        VSUCCEED    = 11    #send change state transaction succeed
        SFAILED     = 12    #stop swap failed
        SSUCCEED    = 13    #stop swap succeed
        COMPLETE    = 128   #change state is confirmed
    
    class statev2b(Enum):
        START       = 0     #no use
        FAILED      = 1     #execute before swap failed, this time can re-execute 
        EFAILED     = 2     #get out amount failed
        ESUCCEED    = 3
        QBFAILED    = 4     #get <to_token_id> blance(swap end) with localdb version, calc diff balance 
        QBSUCCEED   = 5
        FILLFAILED  = 6     #fill map sender failed
        FILLSUCCEED = 7
        PFAILED     = 8     #payment(libra token) failed
        PSUCCEED    = 9     #payment(libra token) succeed
        VFAILED     = 10    #send change state transaction failed
        VSUCCEED    = 11    #send change state transaction succeed
        SFAILED     = 12    #stop swap failed
        SSUCCEED    = 13    #stop swap succeed
        COMPLETE    = 128   #change state is confirmed
    #exc_traceback_objle : info
    class info(__base):
        __tablename__='info'
        version     = Column(Integer, index=True, nullable=False)
        state       = Column(Integer, index=True, nullable=False)
        created     = Column(DateTime, default=datetime.datetime.now)
        times       = Column(Integer, nullable=False, default=1)
        tranid      = Column(String(64), nullable=False, primary_key=True)
        receiver    = Column(String(64), nullable=False)
        detail      = Column(String(256))
    
        def __repr__(self):
            return f"<info(version={self.version}, state={self.state}, created={self.created}, times={self.times}, tranid={self.tranid}, receiver = {self.receiver}, detail={detail})>"

    @property
    def init_state(self):
        return self._inited

    @init_state.setter
    def init_state(self, value):
        self._inited = value

    def __init_db(self, dbfile, create = True, path = None):
        db_echo = False

        if path is not None:
            if not os.path.exists(path):
                os.makedirs(path)
            dbfile = os.path.join(path, dbfile)

        if not create and not os.path.exists(dbfile):
            self._logger.debug(f"not found db({dbfile})")
            self.init_state = False
            return

        self._logger.debug(f"start init_db(dbfile={dbfile})")
        if stmanage.get_db_echo():
            db_echo = stmanage.get_db_echo()

        self.__engine = create_engine('sqlite:///%s?check_same_thread=False' % dbfile, echo=db_echo)
        #self.info.__table__
        self.__base.metadata.create_all(self.__engine)
        Session = sessionmaker(bind=self.__engine)
        self.__session = Session()
        self.init_state = True
    
    def __uninit_db(self):
        pass
        
    def insert(self, version, state, tranid, receiver, detail = ""):
        try:
            data = self.info(version=version,state=state.value, tranid=tranid, receiver = receiver, detail=detail)
            self.__session.add(data)

            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def insert_commit(self, version, state, tranid, receiver, detail = ""):
        try:
            ret = self.insert(version, state, tranid, receiver)
            if ret.state != error.SUCCEED:
                return ret 
            ret = self.commit()
        except Exception as e:
            ret = parse_except(e)
        return ret

    def commit(self):
        try:
            self.__session.flush()
            self.__session.commit()

            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def query(self, tranid):
        proofs = []
        try:
            filter_tranid = (self.info.tranid==tranid)
            proofs = self.__session.query(self.info).filter(filter_tranid).all()
            ret = result(error.SUCCEED, datas = proofs)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def has_info(self, tranid):
        try:
            filter_tranid = (self.info.tranid==tranid)
            state = (self.__session.query(self.info).filter(filter_tranid).count() > 0)
            ret = result(error.SUCCEED, datas = state) 
        except Exception as e:
            ret = parse_except(e)
        return ret

    def is_target_state(self, tranid, state):
        try:
            filter_tranid = (self.info.tranid==tranid)
            filter_state = (self.info.state==state)
            state = (self.__session.query(self.info).filter(filter_tranid).filter(filter_state).count() > 0)
            ret = result(error.SUCCEED, datas = state) 
        except Exception as e:
            ret = parse_except(e)
        return ret

    def __query_state(self, state, maxtimes=999999999):
        proofs = []
        try:
            filter_state = (self.info.state==state.value)
            filter_times = (self.info.times<=maxtimes)
            proofs = self.__session.query(self.info).filter(filter_state).filter(filter_times).all()
            ret = result(error.SUCCEED, datas = proofs)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def query_state_count(self, state):
        try:
            filter_state = (self.info.state==state.value)
            proofs = self.__session.query(self.info).filter(filter_state).count()
            ret = result(error.SUCCEED, datas = proofs)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def query_with_state(self, state, maxtimes = 999999999):
        return self.__query_state(state, maxtimes)

    def query_is_start(self, maxtimes = 999999999):
        return self.__query_state(self.state.START, maxtimes)

    def query_is_succeed(self, maxtimes = 999999999):
        raise "not support"
        #return self.__query_state(self.state.SUCCEED, maxtimes)

    def query_is_failed(self, maxtimes=999999999):
        return self.__query_state(self.state.FAILED, maxtimes)

    def query_is_complete(self, maxtimes=999999999):
        return self.__query_state(self.state.COMPLETE, maxtimes)

    def query_is_vfailed(self, maxtimes=999999999):
        return self.__query_state(self.state.VFAILED, maxtimes)

    def query_is_vsucceed(self, maxtimes = 999999999):
        return self.__query_state(self.state.VSUCCEED, maxtimes)

    def __update(self, tranid, state, detail = ""):
        try:
            inc = 0
            if state in (self.state.FAILED, self.state.EFAILED, self.state.QBFAILED, self.state.FILLFAILED, self.state.PFAILED, self.state.VFAILED, self.state.SFAILED):
                inc = 1
            filter_tranid = (self.info.tranid==tranid)
            if detail:
                datas = self.__session.query(self.info).filter(filter_tranid)\
                        .update({self.info.state:state.value, self.info.times:self.info.times + inc, self.info.detail : detail})
            else:
                datas = self.__session.query(self.info).filter(filter_tranid)\
                        .update({self.info.state:state.value, self.info.times:self.info.times + inc})
            ret = result(error.SUCCEED, datas = datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def __update_commit(self, tranid, state, detail = ""):
        try:
            ret = self.__update(tranid, state, detail)
            if ret.state != error.SUCCEED:
                return ret

            ret = self.commit()
        except Exception as e:
            ret = parse_except(e)
        return ret

    def update_state_commit(self, tranid, state, detail = ""):
        return self.__update_commit(tranid, state, detail)

    def flushinfo(self):
        self.__session.execute("delete from info")

def show_state_count(db, logger):
    ret = db.query_is_start()
    assert ret.state == error.SUCCEED, "query failed."
    logger.debug(f"query_is_start:{ret.datas}")

    ret = db.query_is_succeed()
    assert ret.state == error.SUCCEED, "query failed."
    logger.debug(f"query_is_succeed:{ret.datas}")

    ret = db.query_is_failed()
    assert ret.state == error.SUCCEED, "query failed."
    logger.debug(f"query_is_failed:{ret.datas}")

    ret = db.query_is_complete()
    assert ret.state == error.SUCCEED, "query failed."
    logger.debug(f"query_is_complete:{ret.datas}")

    ret = db.query_is_vfailed()
    assert ret.state == error.SUCCEED, "query failed."
    logger.debug(f"query_is_vfailed:{ret.datas}")

    ret = db.query_is_vsucceed()
    assert ret.state == error.SUCCEED, "query failed."
    logger.debug(f"query_is_vsucceed:{ret.datas}")


def test_dblocal():
    pass
    logger = log.logger.getLogger("test_dblocal")
    db = dblocal("test_dblocal", "test_dblocal.db")
    db.flushinfo()
    tran_id = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    ret = db.insert_commit(
            9, \
            dblocal.state.START, \
            tran_id,            
            "receiver000000000000000000000000"
            )
    assert ret.state == error.SUCCEED, "insert_commit failed."

    db.insert_commit(
            10, \
            dblocal.state.START, \
            "vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv",
            "receiver111111111111111111111111111111111111111111111"
            )
    assert ret.state == error.SUCCEED, "insert_commit failed."

    ret = db.query(tran_id)
    assert ret.state == error.SUCCEED, "query failed."
    logger.debug(f"query result: {ret.datas}")

    logger.debug(f"has info(true):{db.has_info(tran_id)}")
    logger.debug(f"has info(false):{db.has_info('VVVVVVVVVVVVVVVVVVVVVVVVV')}")
    
    show_state_count(db, logger)

    ret = db.update_state_commit(tran_id, dblocal.state.FAILED)
    show_state_count(db, logger)

    ret = db.update_commit(tran_id, dblocal.state.START)
    show_state_count(db, logger)

    ret = db.update_commit(tran_id, dblocal.state.VFAILED)
    show_state_count(db, logger)

    ret = db.update_state_commit(tran_id, dblocal.state.VSUCCEED)
    show_state_count(db, logger)

    ret = db.update_state_commit(tran_id, dblocal.state.COMPLETE)
    show_state_count(db, logger)

if __name__ == "__main__":
    stmanage.set_conf_env("../bvexchange.toml")
    test_dblocal()
