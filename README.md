# RPI Telegram BOT
telegram BOT for RPI Power Management control

Installation
--------------------------

1. #### downoad the require python packages

	>sudo apt-get update

	>sudo apt-get install python3-mysql.connector python3-pexpect
	
	>sudo pip3 install telepot


2. #### Create the /srv folder
	
	>sudo mkdir /srv


3. #### Get the main code

	> cd /srv

	> sudo git clone git@151.98.52.73:Automation/RPIBot.git


Configuration
--------------------------



- Create the log directory

	>sudo mkdir /var/log/RPIBOT

	>sudo chmod 777 -R /var/log/RPIBOT


- Copy the initialization service file

	>sudo cp /srv/xmlrpc/initd /etc/init.d/rpibot

	>sudo chmod +x /etc/init.d/rpibot


- Enable the service

	>sudo systemctl enable rpibot

- Start the service

	>sudo service rpibot start