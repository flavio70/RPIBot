import os
import json
import logging
import logging.config


PKG_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = PKG_DIR


class rpi():
    def __init__(self):
        print('\nRPIBot RPI Object initialization...')
        self.rpi = None
        with open('%s/rpi.json'%PKG_DIR,"r",encoding="utf-8") as fd:
            self.rpi = json.load(fd)


    def getRPI(self):
        return self.rpi



class _logConst():

    LOG_DIR = BASE_DIR + '/logs'
    LOG_SETTINGS = BASE_DIR + '/logging.json'
    ERROR_LOG = LOG_DIR +'/error.log'
    MAIN_LOG = LOG_DIR +'/main.log'

class frmkLog():
    
    def __init__(self):
        c=_logConst()
        print('\nRPIBot Check package base dir: %s\n'%PKG_DIR)
        with open(c.LOG_SETTINGS,"r",encoding="utf-8") as fd:
            D = json.load(fd)
            D.setdefault('version',1)
            logging.config.dictConfig(D)

    def getLogger(self,name):
        
        return logging.getLogger(name)


class botUsers():

    def __init__(self):
        print('\nRPIBot Users initialization...')
        self.users = None
        with open('%s/users.json'%PKG_DIR,"r",encoding="utf-8") as fd:
            self.users = json.load(fd)


    def getUsers(self):
        return self.users


class DB():

    def __init__(self):
        self._DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.mysql',
                'NAME': 'KATE' ,
	            'USER': 'smosql' ,
	            'PASSWORD' : 'sm@ptics' ,
	            'PORT': '3306' ,
	            'HOST': '151.98.52.73'
              }
        }
    def getDB(self):
        return self._DATABASES



