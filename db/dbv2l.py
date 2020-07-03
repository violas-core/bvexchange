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
name="dbv2l"

class dbv2l(baseobject):
    __base = declarative_base()
    __engine = ""
    __session = ""
    __engine = ""

    def __init__(self, name, dbfile):
        baseobject.__init__(self, name)
        self.__init_db(dbfile)

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
        START       = 0  #no use
        SUCCEED     = 1  #send token ok 
        FAILED      = 2  #send map token failed
        VFAILED     = 3  #send change state transaction failed
        VSUCCEED    = 4  #send change state transaction succeed
        COMPLETE    = 128  #change state is confirmed
    
    #exc_traceback_objle : info
    class info(__base):
        __tablename__='v2linfo'
        version     = Column(Integer, index=True, nullable=False)
        state       = Column(Integer, index=True, nullable=False)
        created     = Column(DateTime, default=datetime.datetime.now)
        times       = Column(Integer, nullable=False, default=1)
        tranid      = Column(String(64), nullable=False, primary_key=True)
    
        def __repr__(self):
            return f"<info(version={self.version}, state={self.state}, created={self.created}, times={self.times}, tranid={self.tranid})>"

    def __init_db(self, dbfile):
        self._logger.debug("start __init_db(dbfile={})".format(dbfile))
        db_echo = False

        if stmanage.get_db_echo():
            db_echo = stmanage.get_db_echo()

        self.__engine = create_engine('sqlite:///%s?check_same_thread=False' % dbfile, echo=db_echo)
        #self.info.__table__
        self.__base.metadata.create_all(self.__engine)
        Session = sessionmaker(bind=self.__engine)
        self.__session = Session()
    
    def __uninit_db(self):
        pass
        
    def insert(self, version, state, tranid):
        try:
            self._logger.info(f"start insert(version={version}, state={state.name}, tranid={tranid}") 

            data = self.info(version=version,state=state.value, tranid=tranid)
            self.__session.add(data)

            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def insert_commit(self, version, state, tranid):
        try:
            ret = self.insert(version, state, tranid)
            if ret.state != error.SUCCEED:
                return ret 
            ret = self.commit()
        except Exception as e:
            ret = parse_except(e)
        return ret

    def commit(self):
        try:
            self._logger.debug("start commit")
            self.__session.flush()
            self.__session.commit()

            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def query(self, tranid):
        proofs = []
        try:
            self._logger.debug(f"start query(tranid={tranid})")
            filter_tranid = (self.info.tranid==tranid)
            proofs = self.__session.query(self.info).filter(filter_tranid).all()
            ret = result(error.SUCCEED, datas = proofs)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def has_info(self, tranid):
        try:
            self._logger.debug(f"start has_info(tranid={tranid})")
            filter_tranid = (self.info.tranid==tranid)
            state = (self.__session.query(self.info).filter(filter_tranid).count() > 0)
            ret = result(error.SUCCEED, datas = state) 
        except Exception as e:
            ret = parse_except(e)
        return ret


    def __query_state(self, state, maxtimes=999999999):
        proofs = []
        try:
            self._logger.debug(f"start __query_state(state={state}, maxtimes={maxtimes})")
            filter_state = (self.info.state==state.value)
            filter_times = (self.info.times<=maxtimes)
            proofs = self.__session.query(self.info).filter(filter_state).filter(filter_times).all()
            ret = result(error.SUCCEED, datas = proofs)
            self._logger.debug(f"result: {len(ret.datas)}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def query_state_count(self, state):
        try:
            self._logger.debug(f"start __query_state(state={state})")
            filter_state = (self.info.state==state.value)
            proofs = self.__session.query(self.info).filter(filter_state).count()
            ret = result(error.SUCCEED, datas = proofs)
            self._logger.debug(f"result: {ret.datas}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def query_is_start(self, maxtimes = 999999999):
        return self.__query_state(self.state.START, maxtimes)

    def query_is_succeed(self, maxtimes = 999999999):
        return self.__query_state(self.state.SUCCEED, maxtimes)

    def query_is_failed(self, maxtimes=999999999):
        return self.__query_state(self.state.FAILED, maxtimes)

    def query_is_complete(self, maxtimes=999999999):
        return self.__query_state(self.state.COMPLETE, maxtimes)

    def query_is_vfailed(self, maxtimes=999999999):
        return self.__query_state(self.state.VFAILED, maxtimes)

    def query_is_vsucceed(self, maxtimes = 999999999):
        return self.__query_state(self.state.VSUCCEED, maxtimes)

    def __update(self, tranid, state):
        try:
            self._logger.info(f"start update(tranid={tranid}, state={state})")
            filter_tranid = (self.info.tranid==tranid)
            datas = self.__session.query(self.info).filter(filter_tranid)\
                    .update({self.info.state:state.value, self.info.times:self.info.times + 1})
            ret = result(error.SUCCEED, datas = datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def __update_commit(self, tranid, state):
        try:
            ret = self.__update(tranid, state)
            if ret.state != error.SUCCEED:
                self._logger.error("update_info_commit failed")
                return ret

            ret = self.commit()
        except Exception as e:
            ret = parse_except(e)
        return ret

    def update_to_start_commit(self, tranid):
        return self.__update_commit(tranid, self.state.START)

    def update_to_succeed_commit(self, tranid):
        return self.__update_commit(tranid, self.state.SUCCEED)

    def update_to_failed_commit(self, tranid):
        return self.__update_commit(tranid, self.state.FAILED)

    def update_to_complete_commit(self, tranid):
        return self.__update_commit(tranid, self.state.COMPLETE)

    def update_to_vfailed_commit(self, tranid):
        return self.__update_commit(tranid, self.state.VFAILED)

    def update_to_vsucceed_commit(self, tranid):
        return self.__update_commit(tranid, self.state.VSUCCEED)

    def flushinfo(self):
        self.__session.execute("delete from v2linfo")

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


def test_dbv2l():
    pass
    logger = log.logger.getLogger("test_dbv2l")
    db = dbv2l("test_dbv2l", "test_dbv2l.db")
    db.flushinfo()
    tran_id = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    ret = db.insert_commit(
            9, \
            dbv2l.state.START, \
            tran_id,            
            )
    assert ret.state == error.SUCCEED, "insert_commit failed."

    db.insert_commit(
            10, \
            dbv2l.state.START, \
            "vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv",
            )
    assert ret.state == error.SUCCEED, "insert_commit failed."

    ret = db.query(tran_id)
    assert ret.state == error.SUCCEED, "query failed."
    logger.debug(f"query result: {ret.datas}")

    logger.debug(f"has info(true):{db.has_info(tran_id)}")
    logger.debug(f"has info(false):{db.has_info('VVVVVVVVVVVVVVVVVVVVVVVVV')}")
    
    show_state_count(db, logger)

    ret = db.update_to_failed_commit(tran_id)
    show_state_count(db, logger)

    ret = db.update_to_succeed_commit(tran_id)
    show_state_count(db, logger)

    ret = db.update_to_start_commit(tran_id)
    show_state_count(db, logger)

    ret = db.update_to_vfailed_commit(tran_id)
    show_state_count(db, logger)

    ret = db.update_to_vsucceed_commit(tran_id)
    show_state_count(db, logger)

    ret = db.update_to_complete_commit(tran_id)
    show_state_count(db, logger)

if __name__ == "__main__":
    stmanage.set_conf_env("../bvexchange.toml")
    test_dbv2l()