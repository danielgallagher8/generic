# -*- coding: utf-8 -*-
"""
Created on Sat Mar 27 14:50:14 2021

@author: danie
"""

"""
Generic classes for use in other scripts
"""

#Import relevant libraries

import sys
import pyodbc
import os
import json
import base64
from keepercommander.params import KeeperParams
from keepercommander import api
from datetime import datetime
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


#Define classes

class Passwords:
    
    def __init__(self, name=None, custom=None):
        self.params = KeeperParams()
        self.make_config_file()
        self.read_config_file()
        api.sync_down(self.params)
        self.name = name
        self.info = self.get_login()
        self.username = self.info['secret1']
        self.password = self.info['secret2']
        self.custom = self.get_custom(name=custom)
    
    def read_config_file(self):
        self.params.config_filename = os.path.join(os.path.dirname(sys.argv[0]), 'config.json')
        if os.path.isfile(self.params.config_filename):
            with open(self.params.config_filename, 'r') as f:
                self.params.config = json.load(f)
                if 'user' in self.params.config:
                    self.params.user = self.params.config['user']
                if 'password' in self.params.config:
                    self.params.password = self.params.config['password']
                if 'mfa_token' in self.params.config:
                    self.params.mfa_token = self.params.config['mfa_token']
                if 'server' in self.params.config:
                    self.params.server = self.params.config['server']
                if 'device_id' in self.params.config:
                    device_id = base64.urlsafe_b64decode(self.params.config['device_id'] + '==')
                    self.params.rest_context.device_id = device_id
        return self.params
    
    def make_config_file(self):
        config_file = os.path.join(os.path.dirname(sys.argv[0]), 'config.json')
        if not os.path.exists(config_file):
            user = input('KeeperPassword username:')
            password = input('KeeperPassword password:')
            json_dict = '{"user":"' + user + '", "password":"' + password + '"}'
            with open(config_file, 'w+') as f:
                f.write(json_dict)
                f.close()

    def get_login(self):
        for record in self.params.record_cache:
            string_dict = self.params.record_cache[record]['data_unencrypted'].decode('utf-8')
            json_dict = json.loads(string_dict)
            if self.name == json_dict['title'].lower():
                return json_dict
        return None
    
    def get_custom(self, name):
        custom = self.info['custom']
        for value in custom:
            if value['name'] == name:
                return value['value']
        return None

class SQL:
    
    def __init__(self, driver, server, db, uid, pwd):
        self.driver = driver
        self.server = server
        self.db = db
        self.uid = uid
        self.pwd = pwd
        self.cursor = self.connect()
    
    def connect(self):
        conn = pyodbc.connect('''Driver={};
                                 Server={};
                                 Database={};
                                 Uid={};
                                 Pwd={};'''.format(self.driver, self.server, self.db, self.uid, self.pwd))
        cursor = conn.cursor()
        return cursor
    
    def select(self, table, columns='*', where=None):
        if where==None:
            query = 'SELECT {} FROM {}'.format(columns, table)
        else:
            query = 'SELECT {} FROM {} WHERE {}'.format(columns, table, where)
        self.cursor.execute(query)
        rows = []
        for row in self.cursor:
            r = []
            for a in row:
                r.append(a)
            rows.append(r)
        return rows
    
    def insert(self, table, columns, values):
        query = "INSERT {} ({}) VALUES ({})".format(table, columns, values)
        self.cursor.execute(query)
        self.cursor.commit()
    
    def drop(self, table):
        query = "DROP TABLE {}".format(table)
        self.cursor.execute(query)
        self.cursor.commit()
        
    def create(self, table, columns):
        query = "CREATE TABLE {} ({})".format(table, columns)
        self.cursor.execute(query)
        self.cursor.commit()
    
    def check_table(self, table):
        if self.cursor.tables(table=table, tableType='TABLE').fetchone():
            return True
        else:
            return False

class Logging:
    
    def __init__(self, logfile=None, filename=sys.argv[0]):
        self.logfile = logfile or self.logfile_name()
        self.filename = filename
        self.make_log_file()

    def make_log_file(self):
        if os.path.exists(self.logfile):
            pass
        else:
            with open(self.logfile, "w") as f:
                f.close()
                
    def logfile_name(self):
        today = datetime.now().strftime('%Y%m%d')
        return 'log_{}'.format(today)

    def log(self, error):
        time = datetime.now().strftime('%Y%m%d %H:%M:%S')
        with open(self.logfile, "a+") as f:
            f.write(time + ' - ' + self.filename + ' - ' + error + '\n')
            f.close()

class Mail:
    
    def __init__(self, receivers=None, subject=None, sender=None, password=None, message=None):
        self.sender = sender or 'danga11ag1995@gmail.com'
        self.password = password or self.get_password()
        self.receivers = receivers or self.sender
        self.subject = subject or ''
        self.message = message or ''
        self.send_email()
    
    def get_password(self):
        custom = Passwords('gmail - danga11ag1995').info['custom']
        for val in custom:
            if val['name'] == 'mail_password':
                return val['value']
        return None
    
    def convert_to_html(self):
        message = self.message.replace('\n','<br>')
        html = '<html><head></head><body>' + message + '</body></html>'
        return html
    
    def send_email(self):
        message = MIMEMultipart("alternative")
        message["Subject"] = self.subject
        message["From"] = self.sender
        message["To"] = self.receivers
        html = self.convert_to_html()
        part = MIMEText(html, "html")
        message.attach(part)
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(self.sender, self.password)
            server.sendmail(self.sender, self.receivers, message.as_string())
