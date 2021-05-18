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
name="dbfunds"

class dbfunds(baseobject):
    __base = declarative_base()
    __engine = ""
    __session = ""
    __engine = ""

    def __init__(self, name, dbfile, create = True, path = None):
        baseobject.__init__(self, name)
        self.__init_db(dbfile, create, path)

    def __del__(self):
        self.__uninit_db()

    
    #exc_traceback_objle : info
    class info(__base):
        __tablename__='info'
        tranid      = Column(String(64), nullable=False, primary_key=True)
        chain       = Column(String(64), nullable=False)
        tokenid     = Column(Integer, nullable=False)
        amount      = Column(Integer)
        created     = Column(DateTime, default=datetime.datetime.now)
        receiver    = Column(String(64), nullable=False)
        times       = Column(Integer)
        detail      = Column(String(256))
    
        def __repr__(self):
            return f"info(<tranid={self.tranid}, chain={self.chain}, tokenid={self.tokenid}, \
                    amount={self.amount}, created={self.created}, receiver = {self.receiver}, detail={self.detail})>"

    @property
    def init_state(self):
        return self._inited

    @init_state.setter
    def init_state(self, value):
        self._inited = value

    def __init_db(self, dbfile, create = True, path = None):
        db_echo = False

        path = path if path else "."
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
        
    def insert(self, tranid, chain, tokenid, amount, receiver, detail = ""):
        try:
            data = self.info(tranid=tranid, chain=chain, tokenid=tokenid, amount=amount, receiver = receiver, detail=detail)
            self.__session.add(data)

            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def insert_commit(self, tranid, chain, tokenid, amount, receiver, detail = ""):
        try:
            print(f"insert_commit({tranid})")
            ret = self.insert(tranid, chain, tokenid, amount, receiver, detail)
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

    def __update(self, tranid, amount, detail = ""):
        try:
            filter_tranid = (self.info.tranid==tranid)
            if detail:
                datas = self.__session.query(self.info).filter(filter_tranid)\
                        .update({self.info.amount:amount, self.info.times:self.info.times + 1, self.info.detail : detail})
            else:
                datas = self.__session.query(self.info).filter(filter_tranid)\
                        .update({self.info.amount:amount, self.info.times:self.info.times + 1})
            ret = result(error.SUCCEED, datas = datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def __update_commit(self, tranid, amount, detail = ""):
        try:
            ret = self.__update(tranid, amount, detail)
            if ret.state != error.SUCCEED:
                return ret

            ret = self.commit()
        except Exception as e:
            ret = parse_except(e)
        return ret

    def update_amount_commit(self, tranid, amount, detail = ""):
        return self.__update_commit(tranid, amount, detail)

    def flushinfo(self):
        self.__session.execute("delete from info")

def show_amount(db, tranid):
    ret = db.query(tranid)
    assert ret.state == error.SUCCEED, f"get tranid({tranid} amount failed), {ret.message}"
    print(f"{tranid} amount: {ret.datas[0].amount}")


def test_dbfunds():
    pass
    logger = log.logger.getLogger("test_dbfunds")
    db = dbfunds("test_dbfunds", "test_dbfunds.db")
    db.flushinfo()
    tran_id_0 = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    ret = db.insert_commit(
            tran_id_0,            
            "violas",
            "BTC",
            10000000,
            "receiver000000000000000000000000"
            )
    assert ret.state == error.SUCCEED, "insert_commit failed."

    tran_id = "yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy"
    db.insert_commit(
            tran_id,            
            "BTC",
            "BTC",
            1000000000,
            "receiver111111111111111111111111111111111111111111111"
            )
    assert ret.state == error.SUCCEED, "insert_commit failed."

    ret = db.query(tran_id)
    assert ret.state == error.SUCCEED, "query failed."
    logger.debug(f"query result: {ret.datas}")

    logger.debug(f"has info(true):{db.has_info(tran_id)}")
    logger.debug(f"has info(false):{db.has_info('VVVVVVVVVVVVVVVVVVVVVVVVV')}")

    show_amount(db, tran_id_0)
    show_amount(db, tran_id)
    ret = db.update_amount_commit(tran_id, 100001)
    show_amount(db, tran_id_0)
    show_amount(db, tran_id)

    ret = db.update_amount_commit(tran_id_0, 200001)
    show_amount(db, tran_id_0)
    show_amount(db, tran_id)

if __name__ == "__main__":
    stmanage.set_conf_env("../bvexchange.toml")
    test_dbfunds()
