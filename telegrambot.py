#!/usr/bin/env python3
import os
import sys
import random
import telepot, telepot.api
from time import sleep
import urllib3
import xmlrpc.client
import json
import re
import mysql.connector
import socket


TOKEN='244831841:AAH1k5-ewhkDuRkYyGIknVxsltBBtSpPNAA'
IMG_NAME='none'

happy = u'\U0001F60A'
tool = u'\U0001F527'
ko = u'\U0001F534'
ok = u'\U0001F535'
alert = u'\U000026A0'
temperature = u'\U0001F321'
info = u'\U00002139'
done = u'\U00002714'

POLLING_TIME=60
TEMP_TH = 70.1
SOCKET_TIMEOUT=10
myproxy_url='http://135.245.192.7:8000'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
print(BASE_DIR)
sys.path.append(BASE_DIR + '/..')

from RPIBot import frmkLog
from RPIBot.DBClass import rpiDB

#classes to be used in case of getting data from local json files
#from RPIBot import DB
#from RPIBot import rpi
#from RPIBot import botUsers
#usrList= botUsers()
#myrpi = rpi()


# init logging
currLog=frmkLog()
logger = currLog.getLogger(os.path.basename(__file__))

#init DB Instance
hostDB=rpiDB()




def checkRPI(rpilist):
    ''' check RPI availability for each rpi in rpilist '''
    res=[]
    fl = True
    socket.setdefaulttimeout(SOCKET_TIMEOUT)
    for rpi in rpilist:
        logger.info('%s : %s'%(str(rpi['id']),str(rpi['ip'])))
        try:
            s=xmlrpc.client.ServerProxy('http://%s:8080'%str(rpi['ip']))
            logger.info(s.checkServer())
            res.append('%s %s (Row %i): %s'%(ok,str(rpi['id']),rpi['row'],str(rpi['ip'])))
        except Exception as xxx:
            logger.error(str(xxx))
            fl = False
            res.append('%s %s (Row %i): %s'%(ko,str(rpi['id']),rpi['row'],str(rpi['ip'])))
    socket.setdefaulttimeout(None)
    return (res,fl)
    
    
    


def checkTemperature(rpilist):
    ''' check RPI temperature for each rpi in rpilist '''
    res=[]
    res1=[]
    fl = True
    socket.setdefaulttimeout(SOCKET_TIMEOUT)
    for rpi in rpilist:
        logger.info('%s : %s'%(str(rpi['id']),str(rpi['ip'])))
        try:
            s=xmlrpc.client.ServerProxy('http://%s:8080'%str(rpi['ip']))
            temp=s.getTemperature().replace('"','')
            logger.info('%s (Row %i) Temperature: %s ^C'%(str(rpi['id']),rpi['row'],temp))
            if float(temp) > TEMP_TH:
                fl = False
                res1.append('%s %s (Row %i): KO'%(temperature,str(rpi['id']),rpi['row']))
            else:
                res1.append('%s %s (Row %i): OK'%(temperature,str(rpi['id']),rpi['row']))    
            res.append('%s %s (Row %i): %s C'%(temperature,str(rpi['id']),rpi['row'],temp))
        except Exception as xxx:
            logger.error(str(xxx))
            res.append('%s %s (Row %i): NA'%(temperature,str(rpi['id']),rpi['row']))
            res1.append('%s %s (Row %i): OK'%(temperature,str(rpi['id']),rpi['row']))
    socket.setdefaulttimeout(None)
    return (res,res1,fl)



def getRStatus(rpilist):
	'''get Racks status for each rpi in rpilist'''
	res=[]
	rows={}
	total=0
	totON=0
	totOFF=0
	socket.setdefaulttimeout(SOCKET_TIMEOUT)
	for rpi in rpilist:
		if not rpi['row'] in rows: rows.update({rpi['row']:[0,0]})
		count=0
		countON=0
		countOFF=0
		logger.info(' Get Rack status from %s : %s'%(str(rpi['id']),str(rpi['ip'])))
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
			if count > 0:res.append('%s. %s\tRacks:\t %i %s / %i %s'%(str(rpi['id']),count,countON,ok,countOFF,ko))	
		except Exception as xxx:
			logger.error(str(xxx))
	socket.setdefaulttimeout(None)
	logger.info(rows)
	return (res,total,totON,totOFF,rows)




def setRack(rpi,pin,status,modifier):
    ''' set rack status to on/off '''

    socket.setdefaulttimeout(SOCKET_TIMEOUT)
    res = False
    logger.info('set pin %s to %s (RPI %s)'%(str(pin),status,rpi))
    try:
        s=xmlrpc.client.ServerProxy('http://%s:8080'%str(rpi))
        s.setGPIO([{'gpio':pin,'status':status,'modifier':modifier}])
        res = True
    except Exception as xxx:
        logger.error(str(xxx))
    socket.setdefaulttimeout(None)
    return res





def handle(msg):
    '''message handler for all bot coming messages'''
    global  myrpi
    logger.info(msg)
    chat_id=msg['chat']['id']
    message=msg['text']
    user=msg['chat']['first_name']
    botuser=msg['chat']['first_name']
    user=hostDB.checkUsr(chat_id)[0]

    if user:
        if message =='/start':
            bot.sendMessage(chat_id,'%s Hello from RPI Bot\nPlease send /help command\nfor list of supported commands'%happy)

        elif message == '/help':
            bot.sendMessage(chat_id,'%s List of supported commands \n/start\n/checkrpi\n/getrpitemp\n/getracksbyrpi\n/getracksbyrow\n/seton Rack Row (Rxx yy[A,B])\n/setoff Rack Row (Rxx yy[A,B])'%info)

        elif message == '/checkrpi':
            statusicon = ok
            (res,fl)=checkRPI(myrpi)
            logger.info(str(res))
            mystr=''
            for elem in res: mystr = '%s%s\n'%(mystr,elem)
            if not fl:statusicon = ko
            bot.sendMessage(chat_id,'%s RPI status: %s\n\n%s'%(tool,statusicon,mystr))

        elif message == '/getrpitemp':
            statusicon = ok
            (res,res1,fl)=checkTemperature(myrpi)
            logger.info(str(res))
            mystr=''
            for elem in res: mystr = '%s%s\n'%(mystr,elem)
            if not fl:statusicon = ko
            bot.sendMessage(chat_id,'%s RPI Temperature:\n\n%s'%(tool,mystr))
            
        elif message == '/getracksbyrpi':
            (res,count,totON,totOFF,rows)=getRStatus(myrpi)
            #(res,count,totON,totOFF)=getRStatus([{"id":1,"ip":"151.98.130.155"}])
            logger.info(str(res))
            mystr=''
            for elem in res: mystr = '%s%s\n'%(mystr,elem)
            bot.sendMessage(chat_id,'%s Rack Status:\n\nTOTAL RACKS RETURNED: %i\nStatus: %i %s / %i %s\n\n%s'%(tool,count,totON,ok,totOFF,ko,mystr))

        elif message == '/getracksbyrow':
            (res,count,totON,totOFF,rows)=getRStatus(myrpi)
            #(res,count,totON,totOFF)=getRStatus([{"id":1,"ip":"151.98.130.155"}])
            logger.info(str(res))
            mystr=''
            for elem in rows: mystr = '%sRow %i: %i %s / %i %s\n'%(mystr,elem,rows[elem][0],ok,rows[elem][1],ko)
            bot.sendMessage(chat_id,'%s Rack Status:\n\nTOTAL RACKS RETURNED: %i\nStatus: %i %s / %i %s\n\n%s'%(tool,count,totON,ok,totOFF,ko,mystr))

        elif message == '/seton': bot.sendMessage(chat_id,'%s Bad command format\nUse /seton Rxx yy[A,B]\n i.e. /seton R22 15A'%info)        
        elif re.match('/seton R[0-9]+ [0-9]+[AB]',message):
            res=message.split()
            rackd=hostDB.getRackDetails(res[1].replace('R',''),res[2])
            logger.info(rackd)
            if rackd:
                rpi = rackd[0]['ip']
                pin = rackd[0]['pin']
                row = rackd[0]['row']
                rack = rackd[0]['rack']
                bot.sendMessage(chat_id,'Setting to ON Row %s, rack %s...'%(row,rack))
                if setRack(rpi,pin,'ON',user['username']):
                    bot.sendMessage(chat_id,'%s ...Done!!!'%(done))
                else:
                    bot.sendMessage(chat_id,'%s ...ERROR!!!'%(alert))
            else:
                bot.sendMessage(chat_id,'Row %s, rack %s not found in DB\nMaybe not under RPI control?'%(res[1],res[2]))
                
        elif message == '/setoff': bot.sendMessage(chat_id,'%s Bad command format\nUse /setoff Rxx yy[A,B]\n i.e. /setoff R22 15A'%info)               
        elif re.match('/setoff R[0-9]+ [0-9]+[AB]',message):
            res=message.split()
            rackd=hostDB.getRackDetails(res[1].replace('R',''),res[2])
            logger.info(rackd)
            if rackd:
                rpi = rackd[0]['ip']
                pin = rackd[0]['pin']
                row = rackd[0]['row']
                rack = rackd[0]['rack']
                bot.sendMessage(chat_id,'Setting to OFF Row %s, rack %s...'%(row,rack))
                if setRack(rpi,pin,'OFF',user['username']):
                    bot.sendMessage(chat_id,'%s ...Done!!!'%(done))
                else:
                    bot.sendMessage(chat_id,'%s ...ERROR!!!'%(alert))
            else:
                bot.sendMessage(chat_id,'Row %s, rack %s not found in DB\nMaybe not under RPI control?'%(res[1],res[2]))
                
                
        else:
            bot.sendMessage(chat_id,'%s wrong command'%message)
    else:
        bot.sendMessage(chat_id,'Hi %s. You are not authorized.\nPlease contact Bot administrator.'%botuser)




def manageAlerts():
    #get actual rpi status
    global res0,fl0,rest0,res1t0,flt0
    global  myrpi
    if any(usr['bot_chat_alert'] == 1 for usr in hostDB.getUsrs()):
        (res,fl)=checkRPI(myrpi)
        if not fl:
            #check RPI has at least one RPI Failed
            #compare with previous situation
        
            if res != res0:
                # send maessage just if different
                mystr = ''
                for elem in res: mystr = '%s%s\n'%(mystr,elem)
                for usr in hostDB.getUsrs():
                    if usr['bot_chat_alert']:
                        bot.sendMessage(usr['bot_chat_id'],'%s ALERT\nSome RPI are not responding:\n%s'%(alert,mystr))
        (res0,fl0) = (res,fl)
        
        (rest,res1t,flt)=checkTemperature(myrpi)
        if not flt:
            #at least one RPI crossed the temperature threshold
            #comparing with previus situation
            
            if res1t != res1t0:
                #we have to send a message (situation has changed)
                mystr = ''
                for elem in rest: mystr = '%s%s\n'%(mystr,elem)
                for usr in hostDB.getUsrs():
                    if usr['bot_chat_alert']:
                        bot.sendMessage(usr['bot_chat_id'],'%s ALERT\nSome RPI are in over Temperature:\n%s'%(alert,mystr))


        (rest0,res1t0,flt0) = (rest,res1t,flt)
            
        
        

if __name__ == '__main__':
    global res0,fl0,rest0,res1t0,flt0
    myrpi = hostDB.getRPI()
    

    telepot.api._pools={'default':urllib3.ProxyManager(proxy_url=myproxy_url,num_pools=3,maxsize=10,retries=False,timeout=30),}
    telepot.api._onetime_pool_spec=(urllib3.ProxyManager,dict(proxy_url=myproxy_url, num_pools=1,maxsize=1,retries=False,timeout=30))
    
    bot = telepot.Bot(TOKEN)
    bot.message_loop(handle)

    logger.info('Start polling time %i seconds'%POLLING_TIME)
    (res0,fl0)=checkRPI(myrpi)
    (rest0,res1t0,flt0)=checkTemperature(myrpi)
    while 1:
        manageAlerts()
        sleep(POLLING_TIME)

