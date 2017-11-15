"""
.. module::DBClass
   :platform: Unix
   :synopsis:Class definition for DB Operations

.. moduleauthor:: Flavio Ippolito <flavio.ippolito@sm-optics.com>

"""
import os
import sys
import logging
import logging.config
import _settings
import mysql.connector
from datetime import datetime


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR + '/..')

from RPIBot import frmkLog
from RPIBot.ansicolors import *


# init logging


currLog=frmkLog()
logger = currLog.getLogger(os.path.basename(__file__))



class rpiDB(object):
    '''We use this class for managing MySQL DB access.

    :param str host: MySQl DB Host IP Address
    :param str name: MySql DB Name
    :param str _username: MySql DB User
    :param str _password: MySql DB user password

    '''
    def __init__(self):
        self.host = _settings.DATABASE['HOST']
        self._username = _settings.DATABASE['USER']
        self._password = _settings.DATABASE['PASSWORD']
        self._port = _settings.DATABASE['PORT']
        self.name = _settings.DATABASE['NAME']

    def _connect(self):
        try:
            return mysql.connector.connect(user=self._username,password=self._password,host=self.host,database=self.name,port=self._port)
        except Exception as inst:
            logger.error(ANSI_fail('DBClass._connect\n%s'%str(inst)))
            return False
                        

    def checkUsr(self,chat_id):
        '''get usr from DB'''
        try:
            conn=self._connect()
            cursor=conn.cursor(dictionary=True)
            querystr="SELECT password,is_superuser,username,first_name,last_name,is_staff,is_active,bot_chat_alert FROM auth_user where bot_chat_id = "+str(chat_id)
            cursor.execute(querystr)
            queryres=cursor.fetchall()
            conn.close()
            usr=[]
            for row in queryres:
                usr.append({'username':row["username"],
                       'first_name':row["first_name"],
                       'last_name':row["last_name"],
                       'password':row["password"],
                       'is_superuser':row["is_superuser"],
                       'is_active':row["is_active"],
                       'is_staff':row["is_staff"],
                       'bot_chat_alert':row["bot_chat_alert"],
                      })

            return usr
        
    
        except Exception as inst:
            logger.error(ANSI_fail('DBClass.checkUsr\n%s'%str(inst)))
            return []
            conn.close()





    def getRPI(self):
        '''get all rpi from DB'''
        try:
            conn=self._connect()
            cursor=conn.cursor(dictionary=True)
            querystr="SELECT T_EQUIPMENT.name,IP,row FROM KATE.T_EQUIPMENT JOIN T_NET on (T_EQUIPMENT_id_equipment = id_equipment) JOIN T_EQUIP_TYPE on (id_type = T_EQUIP_TYPE_id_type) JOIN T_LOCATION on (T_LOCATION_id_location = id_location) where T_EQUIP_TYPE.name = 'RPI'"

            cursor.execute(querystr)
            queryres=cursor.fetchall()
            conn.close()
            rpi=[]
            for row in queryres:
                rpi.append({'id':row["name"],'ip':row["IP"],'row':row["row"]})

            return rpi
            
        
    
        except Exception as inst:
            logger.error(ANSI_fail('DBClass.getRPI\n%s'%str(inst)))
            return []
            conn.close()




    def getUsrs(self):
        '''get allowed users from DB'''
        try:
            conn=self._connect()
            cursor=conn.cursor(dictionary=True)
            querystr="SELECT password,is_superuser,username,first_name,last_name,is_staff,is_active,bot_chat_id,bot_chat_alert FROM auth_user where bot_chat_id != 0"

            cursor.execute(querystr)
            queryres=cursor.fetchall()
            conn.close()
            
            usr=[]
            for row in queryres:
                usr.append({'username':row["username"],
                           'first_name':row["first_name"],
                           'last_name':row["last_name"],
                           'password':row["password"],
                           'is_superuser':row["is_superuser"],
                           'is_active':row["is_active"],
                           'is_staff':row["is_staff"],
                           'bot_chat_id':row["bot_chat_id"],
                           'bot_chat_alert':row["bot_chat_alert"],
                          })

            return usr
            
        except Exception as inst:
            logger.error(ANSI_fail('DBClass.getUsrs\n%s'%str(inst)))
            return []
            conn.close()



    def getRackDetails(self,row,rack):
        '''get rack details from DB'''
        try:
            conn=self._connect()
            cursor=conn.cursor(dictionary=True)
            querystr ="SELECT IP,pin,row,rack FROM KATE.T_POWER_MNGMT join T_LOCATION on (T_LOCATION_id_location = id_location) join T_NET using (T_EQUIPMENT_id_equipment) where row = "+row+" and rack = '"+rack+"'"
            cursor.execute(querystr)
            queryres=cursor.fetchall()
            conn.close()
            
            rack=[]
            for r in queryres:
                rack.append({'ip':r["IP"],
                           'pin':r["pin"],
                           'row':r["row"],
                           'rack':r["rack"],
                          })

            return rack

            
        
    
        except Exception as inst:
            logger.error(ANSI_fail('DBClass.getRackDetails\n%s'%str(inst)))
            return []
            conn.close()



