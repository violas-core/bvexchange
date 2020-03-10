#!/usr/bin/python3
'''
btc exchange vbtc db
'''
import operator
import sys, os
sys.path.append(os.getcwd())
sys.path.append("..")
import log
import log.logger
import traceback
import datetime
import stmanage
import random
from comm.error import error
from comm.result import result
from comm.result import parse_except
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime, UniqueConstraint, Index, String
from enum import Enum
from baseobject import baseobject

#module name
name="dbb2v"

class dbb2v(baseobject):
    __base = declarative_base()
    __engine = ""
    __session = ""
    __engine = ""

    def __init__(self, name, dbfile):
        baseobject.__init__(self, name)

        self._logger.debug("start __init__")
        self.__init_db(dbfile)

    def __del__(self):
        self.__uninit_db()

    #btc exchange vbtc state
    class state(Enum):
        START       = 0 #start exchange 
        SUCCEED     = 1 #exchange succeed, but btc blockchain not changed state
        FAILED      = 2 #exchange failed
        SUCCEED_BTC = 3 #exchange succeed, btc blockchain changed state
        FAILED_BTC  = 4 #btc failed
        COMPELETE   = 128 #exchange succeed and btc blockchain changed state
    
    #exc_traceback_objle : b2vinfo
    class b2vinfo(__base):
        __tablename__='b2vinfo'
        txid        = Column(String(64), index=True, nullable=False)
        fromaddress = Column(String(64), index=True, nullable=False)
        toaddress   = Column(String(64), index=True, nullable=False)
        bamount     = Column(Integer, nullable=False)
        vaddress    = Column(String(64), index=True, nullable=False, primary_key=True)
        sequence    = Column(Integer, index=True, nullable=False, primary_key=True)
        vamount     = Column(Integer)
        height      = Column(Integer)
        vtoken       = Column(String(64), nullable=False)
        createblock = Column(String(64), index=True, nullable=False)
        updateblock = Column(String(64), index=True) 
        txid_end    = Column(String(64)) #here is saved update txid
        state       = Column(Integer, index=True, nullable=False)
        created     = Column(DateTime, default=datetime.datetime.now)
        detail      = Column(String(256))

    
        def __repr__(self):
            return "<b2vinfo(txid=%s,fromaddress = %s, toaddress = %s, bamount = %i, vaddress = %s, sequence=%i, \
                    vamount = %i, vtoken = %s, createblock = %s, updateblock = %s, state = %i)>" % (
                    self.txid, self.fromaddress, self.toaddress, self.bamount, self.vaddres, self.sequence, \
                    self.vamount, self.vbt, self.createblock, self.updateblock, self.state)
    
    def __init_db(self, dbfile):
        self._logger.debug("start __init_db")
        db_echo = False

        if stmanage.get_db_echo():
            db_echo = stmanage.get_db_echo()

        self.__engine = create_engine('sqlite:///{}?check_same_thread=False'.format(dbfile), echo=db_echo)
        #self.b2vinfo.__table__
        self.__base.metadata.create_all(self.__engine)
        Session = sessionmaker(bind=self.__engine)
        self.__session = Session()
    
    def __uninit_db(self):
        pass
        
    def insert_b2vinfo(self, vtxid, vfromaddress, vtoaddress, vbamount, vvaddress, vsequence, vvamount, vvtoken, vcreateblock, vupdateblock):
        try:
            self._logger.info(f"start insert_b2vinfo (vtxid={vtxid}, vfromaddress={vfromaddress}, vtoaddress={vtoaddress}, \
                    vbamount={vbamount}, vvaddress={vvaddress}, vsequence={vsequence}, vvamount={vvamount}, vvtoken={vvtoken}, \
                    vcreateblock={vcreateblock}, vupdateblock={vupdateblock}, vstate={self.state.START.name})")

            b2vi = self.b2vinfo(txid=vtxid, fromaddress=vfromaddress, toaddress=vtoaddress, bamount=vbamount, vaddress=vvaddress, sequence=vsequence, \
                vamount=vvamount, vtoken=vvtoken, createblock=vcreateblock, updateblock=vupdateblock, state=self.state.SUCCEED.value, height=0)
            self.__session.add(b2vi)

            ret = result(error.SUCCEED, "", "")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def insert_b2vinfo_commit(self, vtxid, vfromaddress, vtoaddress, vbamount, vvaddress, vsequence, vvamount, vvtoken, vcreateblock, vupdateblock):
        try:
            self._logger.debug("start insert_b2vinfo_commit")
            result = self.insert_b2vinfo(vtxid, vfromaddress, vtoaddress, vbamount, vvaddress, vsequence, vvamount, vvtoken, vcreateblock, vupdateblock)
            if result.state != error.SUCCEED:
                return result
            self.__session.flush()
            ret = self.commit()
        except Exception as e:
            ret = parse_except(e)
        return ret

    def commit(self):
        try:
            self._logger.debug("start commit")
            self.__session.flush()
            self.__session.commit()
            ret = result(error.SUCCEED, "", "")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def query_b2vinfo(self, vaddress, sequence):
        try:
            self._logger.debug(f"start query_b2vinfo(vaddress={vaddress}, sequence={sequence})")
            filter_vaddr = (self.b2vinfo.vaddress==vaddress)
            filter_seq = (self.b2vinfo.sequence==sequence)
            proofs = self.__session.query(self.b2vinfo).filter(filter_seq).filter(filter_vaddr).all()
            ret = result(error.SUCCEED, "", proofs)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def has_b2vinfo(self, vaddress, sequence):
        try:
            self._logger.debug(f"start has_b2vinfo(vaddress={vaddress}, sequence={sequence})")
            filter_vaddr = (self.b2vinfo.vaddress==vaddress)
            filter_seq = (self.b2vinfo.sequence==sequence)
            ret = result(error.SUCCEED, "", self.__session.query(self.b2vinfo).filter(filter_seq).filter(filter_vaddr).count() > 0)
            self._logger.debug(f"result: {ret.datas}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def __query_b2vinfo_state(self, state):
        try:
            self._logger.debug(f"start query_b2vinfo({state.name})")
            filter_state = (self.b2vinfo.state==state.value)
            proofs = self.__session.query(self.b2vinfo).filter(filter_state).all()
            ret = result(error.SUCCEED, "", proofs)
            self._logger.debug(f"result: {len(ret.datas)}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def query_state_count(self, state):
        try:
            self._logger.debug(f"start query_state_count({state.name})")
            filter_state = (self.b2vinfo.state==state.value)
            proofs = self.__session.query(self.b2vinfo).filter(filter_state).count()
            ret = result(error.SUCCEED, "", proofs)
            self._logger.debug(f"result: {ret.datas}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def query_b2vinfo_is_start(self):
        return self.__query_b2vinfo_state(self.state.START)

    def query_b2vinfo_is_succeed(self):
        return self.__query_b2vinfo_state(self.state.SUCCEED)

    def query_b2vinfo_is_failed(self):
        return self.__query_b2vinfo_state(self.state.FAILED)

    def query_b2vinfo_is_complete(self):
        return self.__query_b2vinfo_state(self.state.COMPELETE)

    def query_b2vinfo_is_btcfailed(self):
        return self.__query_b2vinfo_state(self.state.FAILED_BTC)

    def query_b2vinfo_is_btcsucceed(self):
        return self.__query_b2vinfo_state(self.state.SUCCEED_BTC)

    def update_b2vinfo(self, vaddress, sequence, state, height = -1, txid = None):
        try:
            self._logger.info(f"start update_b2vinfo(vaddress={vaddress}, sequence={sequence}, state={state.name}, height={height})")
            filter_vaddr = (self.b2vinfo.vaddress==vaddress)
            filter_seq = (self.b2vinfo.sequence==sequence)
            upn = self.__session.query(self.b2vinfo).filter(filter_seq).filter(filter_vaddr).update({self.b2vinfo.state:state.value})
            if height >= 0:
                upn = self.__session.query(self.b2vinfo).filter(filter_seq).filter(filter_vaddr).update({self.b2vinfo.height:height})
            if txid is not None:
                upn = self.__session.query(self.b2vinfo).filter(filter_seq).filter(filter_vaddr).update({self.b2vinfo.txid_end:txid})

            self.__session.flush()
            self.__session.commit()

            ret = result(error.SUCCEED, "", upn)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def __update_b2vinfo_commit(self, vaddress, sequence, state, height = -1, txid = None):
        try:
            ret = self.update_b2vinfo(vaddress, sequence, state, height, txid)
            if ret != error.SUCCEED:
                return ret

            ret = self.commit()
        except Exception as e:
            ret = parse_except(e)
        return ret

    def update_b2vinfo_to_start_commit(self, vaddress, sequence):
        return self.__update_b2vinfo_commit(vaddress, sequence, self.state.START)

    def update_b2vinfo_to_succeed_commit(self, vaddress, sequence, height):
        return self.__update_b2vinfo_commit(vaddress, sequence, self.state.SUCCEED, height)

    def update_b2vinfo_to_failed_commit(self, vaddress, sequence):
        return self.__update_b2vinfo_commit(vaddress, sequence, self.state.FAILED)

    def update_b2vinfo_to_complete_commit(self, vaddress, sequence):
        return self.__update_b2vinfo_commit(vaddress, sequence, self.state.COMPELETE)

    def update_b2vinfo_to_btcfailed_commit(self, vaddress, sequence):
        return self.__update_b2vinfo_commit(vaddress, sequence, self.state.FAILED_BTC)

    def update_b2vinfo_to_btcsucceed_commit(self, vaddress, sequence, txid):
        return self.__update_b2vinfo_commit(vaddress, sequence, self.state.SUCCEED_BTC, -1, txid)

