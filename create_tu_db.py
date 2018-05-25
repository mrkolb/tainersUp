from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy import Table
from sqlalchemy import Column
from sqlalchemy import Integer, String
from sqlalchemy import or_
from sqlalchemy import select
from sqlalchemy import update
from flask import Flask, session, render_template, g, request, redirect, url_for
from flask_session import Session
from functools import wraps
import datetime
from flask_bcrypt import Bcrypt
#import sys
#import time

app = Flask(__name__)
# Check Configuration section for more details
SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
Session(app)
bcrypt = Bcrypt(app)

##### Database Definition ########
db_uri = 'sqlite:///db.sqlite-tu3'
engine = create_engine(db_uri)

# Create a metadata instance
metadata = MetaData(engine)

'''def spinning_cursor():
    while True:
        for cursor in '|/-\\':
            yield cursor

spinner = spinning_cursor()
for _ in range(50):
    sys.stdout.write(spinner.next())
    sys.stdout.flush()
    time.sleep(0.1)
    sys.stdout.write('\b')'''

accounts = Table('accounts', metadata,
              Column('id', Integer, primary_key=True),
              Column('username', String),
              Column('password', String),
              Column('firstname', String),
              Column('lastname', String),
              Column('creationdate', String),
              Column('pwdreset', Integer))

profiles = Table('profiles', metadata,
              Column('id', Integer, primary_key=True),
              Column('username', String),
              Column('role', String),
              Column('partner', String),
              Column('svc_a', Integer),
              Column('svc_b', Integer),
              Column('svc_c', Integer),
              Column('svc_d', Integer),
              Column('svc_e', Integer),
              Column('svc_f', Integer))

roles = Table('roles', metadata,
              Column('id', Integer, primary_key=True),
              Column('role', String),
              Column('rolename', String))

partners = Table('partners', metadata,
              Column('id', Integer, primary_key=True),
              Column('partner', String),
              Column('partnername', String))

services = Table('services', metadata,
              Column('id', Integer, primary_key=True),
              Column('service', String),
              Column('servicename', String))

issues = Table('issues', metadata,
              Column('id', Integer, primary_key=True),
              Column('partner', String),
              Column('service', String),
              Column('issueDescription', String),
              Column('issueRequestor', String),
              Column('assignment', String),
              Column('updates', String),
              Column('resolved', Integer))

kpi = Table('kpi', metadata,
              Column('id', Integer, primary_key=True),
              Column('partner', String),
              Column('service', String),
              Column('kpiDescription', String),
              Column('kpiMetric', Integer),
              Column('kpiCalc', Integer),
              Column('kpiStatus', String),
              Column('kpiNote',String))

# Create all tables
metadata.create_all()
for _t in metadata.tables:
   print "creating schema_tu2:table ", _t



####  Roles & partners dictionary ######

''' roles = {'admin_role': "admin", 'operator_role': "operator", 'viewer_role': "read_only"}
partners = {'home_company': "Boehringer Ingelheim", 'partner_A': "Accenture", \
 'partner_B': "CapGemini"}'''


# Seed initial data for testing
conn = engine.connect()
conn.execute(roles.insert(),[
   {'role':'admin_role','rolename':'admin'},
   {'role':'operator_role','rolename':'operator'},
   {'role':'viewer_role','rolename':'read_only'}])

conn.execute(partners.insert(),[
   {'partner':'client','partnername':'AjaxCorp'},
   {'partner':'partner_a','partnername':'Accenture'},
   {'partner':'partner_b','partnername':'HP'}])

conn.execute(services.insert(),[
   {'service':'svc_a','servicename':'database'},
   {'service':'svc_b','servicename':'citrix'},
   {'service':'svc_c','servicename':'application'},
   {'service':'svc_d','servicename':'printing'},
   {'service':'svc_e','servicename':'desktop'},
   {'service':'svc_f','servicename':'communications'}])

now = datetime.datetime.now()
password = bcrypt.generate_password_hash('!qaz')
conn.execute(accounts.insert(),[
{'username':'auser','password':password,'firstname':'Able','lastname':'User',\
'creationdate': now.strftime("%Y-%m-%d %H:%M"),'pwdreset':'0'},
{'username':'tuadmin','password':password,'firstname':'TainersUp','lastname':'Administrator',\
'creationdate': now.strftime("%Y-%m-%d %H:%M"),'pwdreset':'0'}])

conn.execute(profiles.insert(),[
{'username':'tuadmin','role':'admin_role','partner':'client','svc_a':'1','svc_b':'1',\
'svc_c':'1','svc_d':'1','svc_e':'0','svc_f':'0'}])
{'username':'auser','role':'operator_role','partner':'partner_a','svc_a':'1','svc_b':'1',\
'svc_c':'1','svc_d':'1','svc_e':'0','svc_f':'0'}])

conn.execute(issues.insert(),[
{'partner':'HP','service':'database','issueDescription':'Backup will not complete','issueRequestor':'akumar',\
'assignment': now.strftime("%Y-%m-%d %H:%M"),'updates':'Waiting for Oracle to respond',\
'resolved':'0'},
{'partner':'Accenture','service':'database','issueDescription':'Merge command will not complete in time alloted','issueRequestor':'fgriffin',\
'assignment': now.strftime("%Y-%m-%d %H:%M"),'updates':'Oracle requests trace file',\
'resolved':'0'}])

conn.execute(kpi.insert(),[
{'partner':'HP','service':'database','kpiDescription':'Meeting Quality','kpiMetric':'95',\
'kpiCalc':'92','kpiStatus':'Amber','kpiNote':'10 events annually'},
{'partner':'Accenture','service':'application','kpiDescription':'Incident in SLA','kpiMetric':'95',\
'kpiCalc':'87','kpiStatus':'Amber','kpiNote':'Incidents in KPI/Total Incidents'}])
