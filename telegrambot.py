#!/usr/bin/env python3
import os
import sys
import random
import telepot, telepot.api
from time import sleep
import urllib3
import xmlrpc.client
import json


TOKEN='244831841:AAH1k5-ewhkDuRkYyGIknVxsltBBtSpPNAA'
IMG_NAME='none'

happy = u'\U0001F60A'
tool = u'\U0001F527'
ko = u'\U0001F534'
ok = u'\U0001F535'
alert = u'\U000026A0'

POLLING_TIME=60
myproxy_url='http://135.245.192.7:8000'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
print(BASE_DIR)
sys.path.append(BASE_DIR + '/..')

from RPIBot import rpi
from RPIBot import DB
from RPIBot import frmkLog
from RPIBot import botUsers

currLog=frmkLog()

logger = currLog.getLogger(os.path.basename(__file__))

usrList= botUsers()
myrpi = rpi()


def getRPI():
    '''get all rpi from DB'''
    currDB=DB().getDB()['default']

    dbConnection=mysql.connector.connect(user=currDB['USER'],password=currDB['PASSWORD'],host=currDB['HOST'],database=currDB['NAME'],port=currDB['PORT'])
    myRecordSet = dbConnection.cursor(dictionary=True)

    SQL="SELECT T_EQUIPMENT.name,IP as name,ip FROM KATE.T_EQUIPMENT JOIN T_NET on (T_EQUIPMENT_id_equipment = id_equipment) JOIN T_EQUIP_TYPE on (id_type = T_EQUIP_TYPE_id_type) where T_EQUIP_TYPE.name = 'RPI'"

    myRecordSet.execute(SQL)

    rpi=[]
    for row in myRecordSet:
        rpi.append({'id':row["name"],'ip':row["ip"]})

    return rpi







def checkRPI(rpilist):
    res=[]
    fl = True
    for rpi in rpilist:
        logger.info('RPI-%s : %s'%(str(rpi['id']),str(rpi['ip'])))
        try:
            s=xmlrpc.client.ServerProxy('http://%s:8080'%str(rpi['ip']))
            logger.info(s.checkServer())
            res.append('%s RPI-%s (Row %i): %s'%(ok,str(rpi['id']),rpi['row'],str(rpi['ip'])))
        except Exception as xxx:
            logger.error(str(xxx))
            fl = False
            res.append('%s RPI-%s (Row %i): %s'%(ko,str(rpi['id']),rpi['row'],str(rpi['ip'])))
    return (res,fl)





def getRStatus(rpilist):
	res=[]
	rows={}
	total=0
	totON=0
	totOFF=0
	for rpi in rpilist:
		if not rpi['row'] in rows: rows.update({rpi['row']:[0,0]})
		count=0
		countON=0
		countOFF=0
		logger.info(' Get Rack status from RPI-%s : %s'%(str(rpi['id']),str(rpi['ip'])))
		try:		
			s=xmlrpc.client.ServerProxy('http://%s:8080'%str(rpi['ip']))
			rstatus=json.loads(s.getGPIOStatus())
			for el in rstatus:
				count +=1
				if el == 1:
					countON +=1
				else:
					countOFF +=1
			total += count
			totOFF += countOFF
			totON += countON
			rows[rpi['row']][0]+=countON
			rows[rpi['row']][1]+=countOFF
			logger.info('%i Racks returned: Racks ON %i. Racks OFF %i'%(count,countON,countOFF))
			if count > 0:res.append('RPI-%s. %s\tRacks:\t %i %s / %i %s'%(str(rpi['id']),count,countON,ok,countOFF,ko))	
		except Exception as xxx:
			logger.error(str(xxx))
	logger.info(rows)
	return (res,total,totON,totOFF,rows)

def handle(msg):
    logger.info(msg)
    chat_id=msg['chat']['id']
    message=msg['text']
    user=msg['chat']['first_name']

    if any(usr['chat_id'] == chat_id for usr in usrList.getUsers()):
        if message =='/start':
            bot.sendMessage(chat_id,'%s Hello from RPI Bot'%happy)

        elif message == '/help':
            bot.sendMessage(chat_id,'List of supported commands \n/start\n/checkrpi\n/getracksbyrpi\n/getracksbyrow')

        elif message == '/checkrpi':
            statusicon = ok
            (res,fl)=checkRPI(myrpi.getRPI())
            logger.info(str(res))
            mystr=''
            for elem in res: mystr = '%s%s\n'%(mystr,elem)
            if not fl:statusicon = ko
            bot.sendMessage(chat_id,'%s RPI status: %s\n\n%s'%(tool,statusicon,mystr))
        elif message == '/getracksbyrpi':
            (res,count,totON,totOFF,rows)=getRStatus(myrpi.getRPI())
            #(res,count,totON,totOFF)=getRStatus([{"id":1,"ip":"151.98.130.155"}])
            logger.info(str(res))
            mystr=''
            for elem in res: mystr = '%s%s\n'%(mystr,elem)
            bot.sendMessage(chat_id,'%s Rack Status:\n\nTOTAL RACKS RETURNED: %i\nStatus: %i %s / %i %s\n\n%s'%(tool,count,totON,ok,totOFF,ko,mystr))

        elif message == '/getracksbyrow':
            (res,count,totON,totOFF,rows)=getRStatus(myrpi.getRPI())
            #(res,count,totON,totOFF)=getRStatus([{"id":1,"ip":"151.98.130.155"}])
            logger.info(str(res))
            mystr=''
            for elem in rows: mystr = '%sRow %i: %i %s / %i %s\n'%(mystr,elem,rows[elem][0],ok,rows[elem][1],ko)
            bot.sendMessage(chat_id,'%s Rack Status:\n\nTOTAL RACKS RETURNED: %i\nStatus: %i %s / %i %s\n\n%s'%(tool,count,totON,ok,totOFF,ko,mystr))
            


        else:
            bot.sendMessage(chat_id,'%s not managed yet'%message)
    else:
        bot.sendMessage(chat_id,'Hi %s. You are not authorized.\nPlease contact Bot administrator.'%user)




def manageAlerts():
    #get actual rpi status
    global res0,fl0
    if any(usr['alert'] == True for usr in usrList.getUsers()):
        (res,fl)=checkRPI(myrpi.getRPI())
        if not fl:
            #check RPI has atlist one RPI Failed
            #compare with previous situation
        
            if res != res0:
                # send maessage just if different
                mystr = ''
                for elem in res: mystr = '%s%s\n'%(mystr,elem)
                for usr in usrList.getUsers():
                    if usr['alert']:
                        bot.sendMessage(usr['chat_id'],'%s ALERT\nSome RPI are not responding:\n%s'%(alert,mystr))
        (res0,fl0) = (res,fl)

if __name__ == '__main__':
    global res0,fl0

    telepot.api._pools={'default':urllib3.ProxyManager(proxy_url=myproxy_url,num_pools=3,maxsize=10,retries=False,timeout=30),}
    telepot.api._onetime_pool_spec=(urllib3.ProxyManager,dict(proxy_url=myproxy_url, num_pools=1,maxsize=1,retries=False,timeout=30))
    
    bot = telepot.Bot(TOKEN)
    bot.message_loop(handle)

    logger.info('Start polling time %i seconds'%POLLING_TIME)
    (res0,fl0)=checkRPI(myrpi.getRPI())
    while 1:
        manageAlerts()
        sleep(POLLING_TIME)

