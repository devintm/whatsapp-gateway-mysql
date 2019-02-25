whatsapp server (gateway) with MySQL
====================================

** WARNING - This may be out of date and may lock the registration of your whats app number. Please, use with caution.


This is the basic set up instructions for registering the phone number and 
receiving whats app messages.  This whats app gateway is connected to Django
web application and creates objects use the Django model objects.


### Technology Stack
	MySQL 5.7.22
	Python 2.7.15 (latest as of 2018-05-11)
	python package - yowsup2 ver. 2.5.7
	python package - MySQL-python ver. 1.2.5


### Resources
	- https://www.digitalocean.com/community/tutorials/how-to-install-mysql-on-ubuntu-16-04
	- https://pypi.org/project/MySQL-python/
	- https://github.com/tgalal/yowsup
	- https://edwards.sdsu.edu/research/installing-mysqldb-module-for-python-2-7-for-ubuntu-12-04/
	- https://iamjagjeetubhi.wordpress.com/2017/09/21/how-to-use-yowsup-the-python-whatsapp-library-in-ubuntu/#step2
	- https://gist.github.com/naiquevin/1746005

### Set Up (Database)

	# Install MySQL server
	$ sudo apt-get update
	$ sudo apt-get install mysql-server
	# Build the dependencies for python-mysqldb libraries 
	$ sudo apt-get build-dep python-mysqldb
	# Setup security setting on MySQL server
	$ mysql_secure_installation
	# Verify MySQL server is working
	$ systemctl status mysql.service
	$ mysqladmin -p -u root version

	# Create MySQL database
	$ mysql -u root -p
	mysql> CREATE DATABASE whatsapp;
	mysql> USE whatsapp;
	mysql> 
CREATE TABLE IF NOT EXISTS messages (
  id int(11) NOT NULL AUTO_INCREMENT,
  sender varchar(45),
  receiver varchar(45),
  message text,
  message_id varchar(45),
  message_type varchar(20),
  message_dt DATETIME(6),
  PRIMARY KEY (id)
);

# DROP TABLE IF EXISTS messages;
INSERT INTO messages(sender, receiver, message, message_id, message_type, message_dt) VALUES 
	("+13001234567", "+13001234567", "Hello world!", "123", "text", '2018-05-11 15:28:00');
SELECT * FROM messages;



	# Install MySQL-python package
	$ pip install MySQL-python


### Set Up (Whatsapp Client)

	# setup virtualenv
	$ python -m virtualenv whatsapp_env
	# Enter the virtualenv
	$ source whatsapp_env/bin/activate
	# Install yowsup with dependencies
	$ pip install yowsup2

    # Configure the yowsup package to use the latest MD5 and version for whatsapp
    # to do the following steps, see- https://iamjagjeetubhi.wordpress.com/2017/09/21/how-to-use-yowsup-the-python-whatsapp-library-in-ubuntu/#step2
    - Download the latest whatsapp .apk from https://www.whatsapp.com/android/

    $ python tools/dexMD5.py ~/Downloads/WhatsApp.apk
    >>> Version: 2.18.141
	>>> ClassesDex: snxBzVEzVfRRYb/tuyGdQA==

	# Enter the above details in the file e.g. /webapps/myproject/lib/python2.7/site-packages/yowsup/env/env_android.py
	yowsup/env/env_android.py

	# WARNING! Make sure you turn OFF the VPN during registration! This could lead to a number ban.

	# Lookup the MCC and MNC codes for your country and region
	# MCC: 310 MNC: 260  T-mobile U.S.
	# UpWork Client
	# 
	# Request code by sms OR ...
	$ yowsup-cli registration --requestcode sms --phone 13001234567 --cc 1 --mcc 310 --mnc 260 --env android

	# Request code by voice
	$ yowsup-cli registration --requestcode voice --phone 13001234567 --cc 1 --mcc 310 --mnc 260 --env android

	# Enter the SMS or Voice code as the register switch value
    $ yowsup-cli registration --register 322239 --phone 13001234567 --cc 1 --env android

    # Save the username (phone number) and the generated password output and put
    # into the creds.py credentials file.


### DevOps Set Up (for systemctl set up)
	# Configure the whatsapp_gateway.service file example

	# Place the whatsapp_gateway.service file in the /etc/systemd/system directory

	# Start the whatsapp gateway service
	$ sudo systemctl start whatsapp_gateway

	# Enable the whatsapp gateway with systemd to happen on startup
	$ sudo systemctl enable whatsapp_gateway



### Demo Client Test
	# This is the echo client, Be careful running this command
	# $ /usr/local/bin/yowsup-cli demos --config config/yowsup-cli.conf --echo

	# This is for the interactive yowsup client
	$ /usr/local/bin/yowsup-cli demos --config config/yowsup-cli.conf --yowsup
	>>> /login 18603170764 bWFvTCR1mahgwrBTrAiHRQ42p84=




