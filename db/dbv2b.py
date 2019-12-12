#!/usr/bin/python3
'''
btc exchange vtoken db
'''
import operator
import sys
sys.path.append("..")
import log
import log.logger
import traceback
import datetime
import sqlalchemy
import setting
import random
from comm.error import error
from comm.result import result
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime, UniqueConstraint, Index, String

from enum import Enum

#module name
name="dbv2b"

#load logging
logger = log.logger.getLogger(name) 

class dbv2b:
    __base = declarative_base()
    __engine = ""
    __session = ""
    __engine = ""
    __traceback_limit = 0

    def __init__(self, dbfile, traceback_limit):
        logger.debug("start __init__")
        self.__traceback_limit = traceback_limit
        self.__init_db(dbfile)

    def __del__(self):
        logger.debug("start dbb2b.__del__")
        self.__uninit_db()

    #btc exchange vtoken state
    class state(Enum):
        START = 0
        SUCCEED = 1
        FAILED = 2
    
    #exc_traceback_objle : v2binfo
    class v2binfo(__base):
        __tablename__='v2binfo'
        txid        = Column(String(64))
        fromaddress = Column(String(64), index=True, nullable=False)
        toaddress   = Column(String(64), index=True, nullable=False)
        bamount     = Column(Integer, nullable=False)
        vaddress    = Column(String(64), index=True, nullable=False, primary_key=True)
        sequence    = Column(Integer, index=True, nullable=False, primary_key=True)
        version     = Column(Integer, index=True, nullable=False, primary_key=True)
        vamount     = Column(Integer, nullable=False)
        vtoken      = Column(String(64), nullable=False)
        vreceiver   = Column(String(64), index=True, nullable=False)
        state       = Column(Integer, index=True, nullable=False)
        created     = Column(DateTime, default=datetime.datetime.now)
    
        def __repr__(self):
            return "<v2binfo(txid=%s,fromaddress={}, toaddress={}, bamount={}, vaddress={}, sequence={}, \
                    vamount={}, vtoken={}, state={}, version={}, vreceiver={})>".format(self.txid, self.fromaddress, self.toaddress, \
                    self.bamount, self.vaddres, self.sequence, self.vamount, self.vtoken, self.state, self.version, self.vreceiver)
    
    class versions(__base):
        __tablename__='versions'
        address     = Column(String(64), index=True, nullable=False, primary_key=True)
        vtoken      = Column(String(64), index=True, nullable=False, primary_key=True)
        version     = Column(Integer, nullable=False) 

        def __repr__(self):
            return "<versions(address=%s, vtoken= %s, version= %i)>" % (self.address, self.module, self.version)

    def __init_db(self, dbfile):
        logger.debug("start __init_db(dbfile={})".format(dbfile))
        db_echo = False

        if setting.db_echo:
            db_echo = setting.db_echo

        self.__engine = create_engine('sqlite:///%s?check_same_thread=False' % dbfile, echo=db_echo)
        #self.v2binfo.__table__
        self.__base.metadata.create_all(self.__engine)
        Session = sessionmaker(bind=self.__engine)
        self.__session = Session()
    
    def __uninit_db(self):
        logger.debug("start __uninit_db")
        
    def insert_v2binfo(self, vtxid, vfromaddress, vtoaddress, vbamount, vvaddress, vsequence, version, vvamount, vvtoken, vreceiver, state):
        try:
            logger.debug("start insert_v2binfo (vtxid={}, vfromaddress={}, vtoaddress={}, vbamount={}, \
                    vvaddress={}, vsequence={}, version={}, vvamount={}, vvtoken={}, vreceiver={}, state={})" \
                    .format(vtxid, vfromaddress, vtoaddress, vbamount, vvaddress, vsequence, version, vvamount, vvtoken, vreceiver, state.name))

            v2bi = self.v2binfo(txid=vtxid, fromaddress=vfromaddress, toaddress=vtoaddress, bamount=vbamount, vaddress=vvaddress, sequence=vsequence, \
                vamount=vvamount, vtoken=vvtoken, state=state.value, version=version, vreceiver=vreceiver)
            self.__session.add(v2bi)

            ret = result(error.SUCCEED, "", "")
        except Exception as e:
            logger.debug(traceback.format_exc(limit=self.__traceback_limit))
            logger.error(str(e))
            ret = result(error.FAILED, str(e), e) 
        return ret

    def insert_v2binfo_commit(self, vtxid, vfromaddress, vtoaddress, vbamount, vvaddress, vsequence, version, vvamount, vvtoken, vreceiver, state):
        try:
            ret = self.insert_v2binfo(vtxid, vfromaddress, vtoaddress, vbamount, vvaddress, vsequence, version, vvamount, vvtoken, vreceiver, state)
            if ret.state != error.SUCCEED:
                return ret 
            ret = self.commit()
        except Exception as e:
            logger.debug(traceback.format_exc(limit=self.__traceback_limit))
            logger.error(str(e))
            ret = result(error.FAILED, str(e), e) 
        return ret

    def commit(self):
        try:
            logger.debug("start commit")
            self.__session.flush()
            self.__session.commit()

            ret = result(error.SUCCEED, "", "")
        except Exception as e:
            logger.debug(traceback.format_exc(limit=self.__traceback_limit))
            logger.error(str(e))
            ret = result(error.FAILED, str(e), e) 
        return ret

    def query_v2binfo(self, vaddress, sequence):
        proofs = []
        try:
            logger.debug("start query_v2binfo(vaddress={}, sequence={})".format(vaddress, sequence))
            filter_vaddr = (self.v2binfo.vaddress==vaddress)
            filter_seq = (self.v2binfo.sequence==sequence)
            proofs = self.__session.query(self.v2binfo).filter(filter_seq).filter(filter_vaddr).all()
            ret = result(error.SUCCEED, "", proofs)
        except Exception as e:
            logger.debug(traceback.format_exc(limit=self.__traceback_limit))
            logger.error(str(e))
            ret = result(error.FAILED, str(e), e) 
        return ret

    def has_v2binfo(self, vaddress, sequence):
        try:
            logger.debug("start has_v2binfo(vaddress={}, sequence={})".format(vaddress, sequence))
            filter_vaddr = (self.v2binfo.vaddress==vaddress)
            filter_seq = (self.v2binfo.sequence==sequence)
            state = (self.__session.query(self.v2binfo).filter(filter_seq).filter(filter_vaddr).count() > 0)
            ret = result(error.SUCCEED, "", state) 
        except Exception as e:
            logger.debug(traceback.format_exc(limit=self.__traceback_limit))
            logger.error(str(e))
            ret = result(error.FAILED, str(e), e) 
        return ret


    def __query_v2binfo_state(self, state):
        proofs = []
        try:
            logger.debug("start __query_v2binfo_state(state={})".format(state.name))
            filter_state = (self.v2binfo.state==state.value)
            proofs = self.__session.query(self.v2binfo).filter(filter_state).all()
            ret = result(error.SUCCEED, "", proofs)
        except Exception as e:
            logger.debug(traceback.format_exc(limit=self.__traceback_limit))
            logger.error(str(e))
            ret = result(error.FAILED, str(e), e) 
        return ret

    def query_v2binfo_is_start(self):
        return self.__query_v2binfo_state(self.state.START)

    def query_v2binfo_is_succeed(self):
        return self.__query_v2binfo_state(self.state.SUCCEED)

    def query_v2binfo_is_failed(self):
        return self.__query_v2binfo_state(self.state.FAILED)

    def update_v2binfo(self, vaddress, sequence, state, txid):
        try:
            logger.debug("start update_v2binfo(vaddress={}, sequence={}, state={}, txid={})".format(state.name, vaddress, sequence, txid))
            filter_vaddr = (self.v2binfo.vaddress==vaddress)
            filter_seq = (self.v2binfo.sequence==sequence)
            datas = self.__session.query(self.v2binfo).filter(filter_seq).filter(filter_vaddr).update({self.v2binfo.state:state.value, self.v2binfo.txid:txid})
            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            logger.debug(traceback.format_exc(limit=self.__traceback_limit))
            logger.error(str(e))
            ret = result(error.FAILED, str(e), e) 
        return ret

    def update_v2binfo_to_succeed(self, vaddress, sequence, txid = None):
        return self.update_v2binfo(vaddress, sequence, self.state.SUCCEED, txid)

    def update_v2binfo_to_failed(self, vaddress, sequence, txid = None):
        return self.pdate_v2binfo(vaddress, sequence, self.state.FAILED, txid)

    def __update_v2binfo_commit(self, vaddress, sequence, state, txid = None):
        try:
            ret = self.update_v2binfo(vaddress, sequence, state)
            if ret != error.SUCCEED:
                return ret

            ret = self.commit()
        except Exception as e:
            logger.debug(traceback.format_exc(limit=self.__traceback_limit))
            logger.error(str(e))
            ret = result(error.FAILED, str(e), e) 
        return ret

    def update_v2binfo_to_start_commit(self, vaddress, sequence, txid = None):
        return self.__update_v2binfo_commit(vaddress, sequence, self.state.START, txid)

    def update_v2binfo_to_succeed_commit(self, vaddress, sequence, txid = None):
        return self.__update_v2binfo_commit(vaddress, sequence, self.state.SUCCEED, txid)

    def update_v2binfo_to_failed_commit(self, vaddress, sequence, txid = None):
        return self.__update_v2binfo_commit(vaddress, sequence, self.state.FAILED, txid)

    def insert_latest_version(self, address, vtoken, version):
        try:
            logger.debug("start insert_latest_version (address={}, vtoken={}, version={})".format(address, vtoken, version))

            v2bi = self.versions(address=address, vtoken=vtoken, version=version)
            self.__session.add(v2bi)
            ret = result(error.SUCCEED, "", "")
        except Exception as e:
            logger.debug(traceback.format_exc(limit=self.__traceback_limit))
            logger.error(str(e))
            ret = result(error.FAILED, str(e), e) 
        return ret

    def insert_latest_version_commit(self, address, vtoken, version):
        try:
            ret = self.insert_latest_version(address, vtoken, version)
            if ret.state != error.SUCCEED:
                return ret 
            ret = self.commit()
        except Exception as e:
            logger.debug(traceback.format_exc(limit=self.__traceback_limit))
            logger.error(str(e))
            ret = result(error.FAILED, str(e), e) 
        return ret

    def query_latest_version(self, address, vtoken):
        proofs = []
        try:
            logger.debug("start query_latest_version(address={}, vtoken={})".format(address, vtoken))
            filter_address = (self.versions.address==address)
            filter_vtoken = (self.versions.vtoken==vtoken)
            info = self.__session.query(self.versions).filter(filter_address).filter(filter_vtoken).all()
            if info is not None and len(info) > 0:
                ret = result(error.SUCCEED, "", info[0].version)
            else:
                ret = result(error.SUCCEED, "", 0)

        except Exception as e:
            logger.debug(traceback.format_exc(limit=self.__traceback_limit))
            logger.error(str(e))
            ret = result(error.FAILED, str(e), e) 
        return ret

    def update_version(self, address, vtoken, version):
        try:
            logger.debug("start update_version(address={}, vtoken={}, version={})".format(address, vtoken, version))
            filter_address = (self.versions.address==address)
            filter_vtoken = (self.versions.vtoken==vtoken)
            datas = self.__session.query(self.versions).filter(filter_address).filter(filter_vtoken).update({self.versions.version:version})
            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            logger.debug(traceback.format_exc(limit=self.__traceback_limit))
            logger.error(str(e))
            ret = result(error.FAILED, str(e), e) 
        return ret

    def update_version_commit(self, address, vtoken, version):
        try:
            ret = self.update_version(address, vtoken, version)
            if ret != error.SUCCEED:
                return ret

            ret = self.commit()
        except Exception as e:
            logger.debug(traceback.format_exc(limit=self.__traceback_limit))
            logger.error(str(e))
            ret = result(error.FAILED, str(e), e) 
        return ret

    def has_version(self, address, vtoken):
        try:
            logger.debug("start has_version(address={}, vtoken={})".format(address, vtoken))
            filter_address = (self.versions.address==address)
            filter_vtoken = (self.versions.vtoken==vtoken)
            datas = self.__session.query(self.versions).filter(filter_address).filter(filter_vtoken).count() > 0
            ret = result(error.SUCCEED, "", datas) 
        except Exception as e:
            logger.debug(traceback.format_exc(limit=self.__traceback_limit))
            logger.error(str(e))
            ret = result(error.FAILED, str(e), e) 
        return ret

    def update_or_insert_version_commit(self, address, vtoken, version):
        try:
            ret = self.has_version(address, vtoken)
            if(ret.state != error.SUCCEED):
                return ret

            if (ret.datas == True):
                ret = self.update_version(address, vtoken, version)
            else:
                ret = self.insert_latest_version_commit(address, vtoken, version)
             
            if ret.state == error.SUCCEED:
                self.commit()
        except Exception as e:
            logger.debug(traceback.format_exc(limit=self.__traceback_limit))
            logger.error(str(e))
            ret = result(error.FAILED, str(e), e) 
        return ret

dbfile = "bve_v2b.db"
traceback_limit = setting.traceback_limit
max_seq = 100000
def test_dbv2b_insert():
    v2b = dbv2b(dbfile, traceback_limit)
    sequence = random.randint(0,max_seq)
    if v2b.has_v2binfo("c8b9311393966d5b64919d73c3d27d88f7f5744ff2fc288f0177761fe0671ca2", sequence):
        return
    v2b.insert_v2binfo("0000000000000000000000000000000000000000000000000000000000000001", \
                "2NFMbhLACujsHKa45X4P2fZupVrgB268pbo", \
                "2NFMbhLACujsHKa45X4P2fZupVrgB268pbo", \
                1, \
                "c8b9311393966d5b64919d73c3d27d88f7f5744ff2fc288f0177761fe0671ca2", \
                sequence, #sequence 
                0, \
                "0000000000000000000000000000000000000000000000000000000000000000", \
                )
    v2b.commit()

def test_dbv2b_query():
    try:
        logger.debug("*****************************************start test_dbv2b_query*****************************************")
        v2b = dbv2b(dbfile, traceback_limit)
        sequence = random.randint(0, max_seq)
        ret = v2b.query_v2binfo("c8b9311393966d5b64919d73c3d27d88f7f5744ff2fc288f0177761fe0671ca2", sequence)

        if ret.state != error.SUCCEED:
            return

        if(len(ret.datas) == 0):
            logger.debug("not fount proof")

        for proof in ret.datas:
            logger.info("vaddress: %s" % (proof.vaddress))
            logger.info("sequence: %s" % (proof.sequence))
            logger.info("state : %i" % (proof.state))
    except Exception as e:
        logger.error(traceback.format_exc(limit=traceback_limit))

def test_dbv2b_query_state_start():
    try:
        logger.debug("*****************************************start test_dbv2b_query_state_start****************************")
        v2b = dbv2b(dbfile, traceback_limit)
        ret = v2b.query_v2binfo_is_start()

        if ret.state != error.SUCCEED:
            return

        if(len(ret.datas) == 0):
            logger.debug("not fount proof")

        for proof in ret.datas:
            logger.info("vaddress: %s" % (proof.vaddress))
            logger.info("sequence: %s" % (proof.sequence))
            logger.info("state : %i" % (proof.state))
    except Exception as e:
        logger.error(traceback.format_exc(limit=traceback_limit))

def test_dbv2b_query_state_succeed():
    try:
        logger.debug("*****************************************start test_dbv2b_query_state_succeed*************************")
        v2b = dbv2b(dbfile, traceback_limit)
        ret = v2b.query_v2binfo_is_succeed()

        if ret.state != error.SUCCEED:
            return

        if(len(ret.datas) == 0):
            logger.debug("not fount proof")

        for proof in ret.datas:
            logger.info("vaddress: %s" % (proof.vaddress))
            logger.info("sequence: %s" % (proof.sequence))
            logger.info("state : %i" % (proof.state))
    except Exception as e:
        logger.error(traceback.format_exc(limit=traceback_limit))

def test_dbv2b_query_state_failed():
    try:
        logger.debug("*****************************************start test_dbv2b_query_state_failed*************************")
        v2b = dbv2b(dbfile, traceback_limit)
        ret = v2b.query_v2binfo_is_failed()

        if ret.state != error.SUCCEED:
            return

        if(len(ret.datas) == 0):
            logger.debug("not fount proof")

        for proof in ret.datas:
            logger.info("vaddress: %s" % (proof.vaddress))
            logger.info("sequence: %s" % (proof.sequence))
            logger.info("state : %i" % (proof.state))
    except Exception as e:
        logger.error(traceback.format_exc(limit=traceback_limit))


def test_dbv2b_update():
    try:
        logger.debug("*****************************************start t_dbv2b_update***************************************")
        v2b = dbv2b(dbfile, traceback_limit)
        sequence = random.randint(0, max_seq)
        v2b.update_v2binfo_to_succeed_commit("c8b9311393966d5b64919d73c3d27d88f7f5744ff2fc288f0177761fe0671ca2", sequence)
    except Exception as e:
        logger.error(traceback.format_exc(limit=traceback_limit))

def test():
    try:
        test_dbv2b_insert()
        test_dbv2b_query()
        test_dbv2b_update()
        test_dbv2b_query()
        test_dbv2b_query_state_start()
        test_dbv2b_query_state_succeed()
        test_dbv2b_query_state_failed()
    except Exception as e:
        logger.error(traceback.format_exc(limit=traceback_limit))

if __name__ == "__main__" :
    test()
