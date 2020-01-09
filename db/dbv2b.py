#!/usr/bin/python3
'''
btc exchange vtoken db
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
from comm.error import error
from comm.result import result
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime, UniqueConstraint, Index, String

from baseobject import baseobject
from enum import Enum

#module name
name="dbv2b"

class dbv2b(baseobject):
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
    ##SUCCEED->COMPLETE
    ##SUCCEED->VFAILED->SUCCEED->COMPLETE
    ##FAILED->SUCCEED->COMPLETE
    ##FAILED->SUCCEED->VFAILED->SUCCEED->COMPLETE
    class state(Enum):
        START       = 0  #no use
        SUCCEED     = 1  #send btc ok and send change state transaction succeed but not confirm
        FAILED      = 2  #send btc failed
        VFAILED     = 3  #send change state transaction failed
        VSUCCEED    = 4  #send change state transaction succeed
        COMPLETE    = 6  #change state is confirmed
    
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
        times       = Column(Integer, nullable=False, default=1)
        tranid      = Column(String(64), nullable=False, primary_key=True)
    
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
        self._logger.debug("start __init_db(dbfile={})".format(dbfile))
        db_echo = False

        if stmanage.get_db_echo():
            db_echo = stmanage.get_db_echo()

        self.__engine = create_engine('sqlite:///%s?check_same_thread=False' % dbfile, echo=db_echo)
        #self.v2binfo.__table__
        self.__base.metadata.create_all(self.__engine)
        Session = sessionmaker(bind=self.__engine)
        self.__session = Session()
    
    def __uninit_db(self):
        pass
        
    def insert_v2binfo(self, vtxid, vfromaddress, vtoaddress, vbamount, vvaddress, vsequence, version, vvamount, vvtoken, vreceiver, state, tranid):
        try:
            self._logger.debug("start insert_v2binfo (vtxid={}, vfromaddress={}, vtoaddress={}, vbamount={}, \
                    vvaddress={}, vsequence={}, version={}, vvamount={}, vvtoken={}, vreceiver={}, state={}, tranid={})" \
                    .format(vtxid, vfromaddress, vtoaddress, vbamount, vvaddress, vsequence, version, vvamount, vvtoken, vreceiver, state.name, tranid))

            v2bi = self.v2binfo(txid=vtxid, fromaddress=vfromaddress, toaddress=vtoaddress, bamount=vbamount, vaddress=vvaddress, sequence=vsequence, \
                vamount=vvamount, vtoken=vvtoken, state=state.value, version=version, vreceiver=vreceiver, tranid=tranid)
            self.__session.add(v2bi)

            ret = result(error.SUCCEED, "", "")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def insert_v2binfo_commit(self, vtxid, vfromaddress, vtoaddress, vbamount, vvaddress, vsequence, version, vvamount, vvtoken, vreceiver, state, tranid):
        try:
            ret = self.insert_v2binfo(vtxid, vfromaddress, vtoaddress, vbamount, vvaddress, vsequence, version, vvamount, vvtoken, vreceiver, state, tranid)
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

            ret = result(error.SUCCEED, "", "")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def query_v2binfo(self, tranid):
        proofs = []
        try:
            self._logger.debug("start query_v2binfo(tranid={})".format(tranid))
            filter_tranid = (self.v2binfo.tranid==tranid)
            proofs = self.__session.query(self.v2binfo).filter(filter_tranid).all()
            ret = result(error.SUCCEED, "", proofs)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def has_v2binfo(self, tranid):
        try:
            self._logger.debug("start has_v2binfo(tranid={})".format(tranid))
            filter_tranid = (self.v2binfo.tranid==tranid)
            state = (self.__session.query(self.v2binfo).filter(filter_tranid).count() > 0)
            ret = result(error.SUCCEED, "", state) 
        except Exception as e:
            ret = parse_except(e)
        return ret


    def __query_v2binfo_state(self, state, maxtimes=999999999):
        proofs = []
        try:
            self._logger.debug("start __query_v2binfo_state(state={}, maxtimes={})".format(state.name, maxtimes))
            filter_state = (self.v2binfo.state==state.value)
            filter_times = (self.v2binfo.times<=maxtimes)
            proofs = self.__session.query(self.v2binfo).filter(filter_state).filter(filter_times).all()
            ret = result(error.SUCCEED, "", proofs)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def query_v2binfo_is_start(self, maxtimes = 999999999):
        return self.__query_v2binfo_state(self.state.START, maxtimes)

    def query_v2binfo_is_succeed(self, maxtimes = 999999999):
        return self.__query_v2binfo_state(self.state.SUCCEED, maxtimes)

    def query_v2binfo_is_failed(self, maxtimes=999999999):
        return self.__query_v2binfo_state(self.state.FAILED, maxtimes)

    def query_v2binfo_is_complete(self, maxtimes=999999999):
        return self.__query_v2binfo_state(self.state.COMPLETE, maxtimes)

    def query_v2binfo_is_vfailed(self, maxtimes=999999999):
        return self.__query_v2binfo_state(self.state.VFAILED, maxtimes)

    def query_v2binfo_is_vsucceed(self, maxtimes = 999999999):
        return self.__query_v2binfo_state(self.state.VSUCCEED, maxtimes)

    def __update_v2binfo(self, tranid, state, txid):
        try:
            self._logger.debug(f"start update_v2binfo(tranid={tranid}, state={state}, txid={txid})")
            filter_tranid = (self.v2binfo.tranid==tranid)
            datas = self.__session.query(self.v2binfo).filter(filter_tranid)\
                    .update({self.v2binfo.state:state.value, self.v2binfo.txid:txid, self.v2binfo.times:self.v2binfo.times + 1})
            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def __update_v2binfo_commit(self, tranid, state, txid = ""):
        try:
            ret = self.__update_v2binfo(tranid, state, txid)
            if ret.state != error.SUCCEED:
                self._logger.debug("update_v2binfo_commit failed")
                return ret

            ret = self.commit()
        except Exception as e:
            ret = parse_except(e)
        return ret

    def update_v2binfo_to_start_commit(self, tranid, txid = ""):
        return self.__update_v2binfo_commit(tranid, self.state.START, txid)

    def update_v2binfo_to_succeed_commit(self, tranid, txid = ""):
        return self.__update_v2binfo_commit(tranid, self.state.SUCCEED, txid)

    def update_v2binfo_to_failed_commit(self, tranid, txid = ""):
        return self.__update_v2binfo_commit(tranid, self.state.FAILED, txid)

    def update_v2binfo_to_complete_commit(self, tranid, txid = ""):
        return self.__update_v2binfo_commit(tranid, self.state.COMPLETE, txid)

    def update_v2binfo_to_vfailed_commit(self, tranid, txid = ""):
        return self.__update_v2binfo_commit(tranid, self.state.VFAILED, txid)

    def update_v2binfo_to_vsucceed_commit(self, tranid, txid = ""):
        return self.__update_v2binfo_commit(tranid, self.state.VSUCCEED, txid)
    
    def insert_latest_version(self, address, vtoken, version):
        try:
            self._logger.debug("start insert_latest_version (address={}, vtoken={}, version={})".format(address, vtoken, version))

            v2bi = self.versions(address=address, vtoken=vtoken, version=version)
            self.__session.add(v2bi)
            ret = result(error.SUCCEED, "", "")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def insert_latest_version_commit(self, address, vtoken, version):
        try:
            ret = self.insert_latest_version(address, vtoken, version)
            if ret.state != error.SUCCEED:
                return ret 
            ret = self.commit()
        except Exception as e:
            ret = parse_except(e)
        return ret

    def query_latest_version(self, address, vtoken):
        proofs = []
        try:
            self._logger.debug("start query_latest_version(address={}, vtoken={})".format(address, vtoken))
            filter_address = (self.versions.address==address)
            filter_vtoken = (self.versions.vtoken==vtoken)
            info = self.__session.query(self.versions).filter(filter_address).filter(filter_vtoken).all()
            if info is not None and len(info) > 0:
                ret = result(error.SUCCEED, "", info[0].version)
                self._logger.debug(f"latest version:{info[0].version}")
            else:
                ret = result(error.SUCCEED, "", 0)

        except Exception as e:
            ret = parse_except(e)
        return ret

    def update_version(self, address, vtoken, version):
        try:
            self._logger.debug("start update_version(address={}, vtoken={}, version={})".format(address, vtoken, version))
            filter_address = (self.versions.address==address)
            filter_vtoken = (self.versions.vtoken==vtoken)
            datas = self.__session.query(self.versions).filter(filter_address).filter(filter_vtoken).update({self.versions.version:version})
            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def update_version_commit(self, address, vtoken, version):
        try:
            ret = self.update_version(address, vtoken, version)
            if ret.state != error.SUCCEED:
                return ret

            ret = self.commit()
        except Exception as e:
            ret = parse_except(e)
        return ret

    def has_version(self, address, vtoken):
        try:
            self._logger.debug("start has_version(address={}, vtoken={})".format(address, vtoken))
            filter_address = (self.versions.address==address)
            filter_vtoken = (self.versions.vtoken==vtoken)
            datas = self.__session.query(self.versions).filter(filter_address).filter(filter_vtoken).count() > 0
            ret = result(error.SUCCEED, "", datas) 
        except Exception as e:
            ret = parse_except(e)
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
            ret = parse_except(e)
        return ret

