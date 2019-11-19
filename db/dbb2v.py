#!/usr/bin/python3
'''
'''
import operator
import sys
sys.path.append('..')
import log.logger
import traceback
import datetime
import sqlalchemy
import setting
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime, UniqueConstraint, Index, String

#load logging
logger = log.logger.getLogger() 

class dbb2v:
    __base = declarative_base()
    __engine = ""
    __session = ""
    __engine = ""
    __traceback_limit = 0

    def __init__(self, dbfile, traceback_limit):
        self.__traceback_limit = traceback_limit
        self.init_db(dbfile)

    #table : b2vinfo
    class b2vinfo(__base):
        __tablename__='b2vinfo'
        txid = Column(String(64), index=True, nullable=False)
        fromaddress = Column(String(64), index=True, nullable=False)
        toaddress = Column(String(64), index=True, nullable=False)
        sequence = Column(Integer)
        bamount = Column(Integer, nullable=False)
        vaddress = Column(String(64), index=True, nullable=False, primary_key=True)
        vamount = Column(Integer, index=True, nullable=False, primary_key=True)
        vbtc = Column(String(64), nullable=False)
        createblock = Column(String(64), index=True, nullable=False)
        updateblock = Column(String(64), index=True)
        state = Column(Integer, index=True, nullable=False)
    
        def __repr__(self):
            return "<b2vinfo(txid=%s,fromaddress = %s, toaddress = %s, bamount = %i, vaddress = %s, sequence=%i, \
                    vamount = %i, vbtc = %s, createblock = %s, updateblock = %s, state = %i)>" % (
                    self.txid, self.fromaddress, self.toaddress, self.bamount, self.vaddres, self.sequence, \
                    self.vamount, self.vbt, self.createblock, self.updateblock, self.state)
    
    def init_db(self, dbfile):
        self.__engine = create_engine('sqlite:///%s?check_same_thread=False' % dbfile, echo=True)
        #self.b2vinfo.__table__
        self.__base.metadata.create_all(self.__engine)
        Session = sessionmaker(bind=self.__engine)
        self.__session = Session()
    
    def insert_b2vinfo(self, vtxid, vfromaddress, vtoaddress, vbamount, vvaddress, vsequence, vvamount, vvbtc, vcreateblock, vupdateblock, vstate):
        try:
            b2vi = self.b2vinfo(txid=vtxid, fromaddress=vfromaddress, toaddress=vtoaddress, bamount=vbamount, vaddress=vvaddress, sequence=vsequence, \
                vamount=vvamount, vbtc=vvbtc, createblock=vcreateblock, updateblock=vupdateblock, state=vstate)
            self.__session.add(b2vi)

            return True
        except Exception as e:
            logger.error(traceback.format_exc(limit=self.__traceback_limit))
        return False

    def commit(self):
        try:
            self.__session.commit()
        except Exception as e:
            logger.error(traceback.format_exc(limit=self.__traceback_limit))
        return False

def test_dbb2v():
    b2v = dbb2v("bve_b2v.db", setting.traceback_limit)
    b2v.insert_b2vinfo("0000000000000000000000000000000000000000000000000000000000000001", \
                "2NFMbhLACujsHKa45X4P2fZupVrgB268pbo", \
                "2NFMbhLACujsHKa45X4P2fZupVrgB268pbo", \
                1, \
                "c8b9311393966d5b64919d73c3d27d88f7f5744ff2fc288f0177761fe0671ca2", \
                2, #sequence 
                0, \
                "0000000000000000000000000000000000000000000000000000000000000000", \
                "e36d8ad4f1ab2ecbaf63d14ac150d464d81ef0fdf45ad0df8c27efaf8a10410d", \
                "e36d8ad4f1ab2ecbaf63d14ac150d464d81ef0fdf45ad0df8c27efaf8a10410d", \
                1)
    b2v.commit()


if __name__ == "__main__" :
    test_dbb2v()
