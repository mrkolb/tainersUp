#! flask/bin/python
from flask import Flask, flash, redirect, render_template, request, session, abort
from flask import url_for, send_from_directory, g
from flask_session import Session
from functools import wraps
from werkzeug import secure_filename
import os
import sys
import subprocess
from flask_bcrypt import Bcrypt
from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy import Table
from sqlalchemy import Column
from sqlalchemy import Integer, String
from sqlalchemy import or_
from sqlalchemy import and_
from sqlalchemy import select
from sqlalchemy import update
from itertools import izip
import datetime


##### Database Definition ########
db_uri = 'sqlite:///db.sqlite-tu3'
engine = create_engine(db_uri)
metadata = MetaData(engine,reflect=True)
act = metadata.tables['accounts']
prof = metadata.tables['profiles']
prtnr = metadata.tables['partners']
svcs = metadata.tables['services']
rolls = metadata.tables['roles']
kpi = metadata.tables['kpi']
issu = metadata.tables['issues']


##### App configuration #######
app = Flask(__name__)
bcrypt = Bcrypt(app)
#####flask_session config########
SESSION_TYPE = 'filesystem'
SESSION_PERMANENT = 'FALSE'
SESSION_FILE_DIR = 'uinfo'
SESSION_FILE_THRESHOLD = '100'
app.config.from_object(__name__)
app.secret_key = os.urandom(12)
Session(app)

#####file upload definition #######
# Path to the upload directory
app.config['UPLOAD_FOLDER'] = 'uploads/'
# Extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set(['yml', 'yaml'])
# Return whether it's an allowed type or not with an exception for "Dockerfile"
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS'] or filename == "Dockerfile"

##### Wrap configuration for flask_session riles #######
def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        conn = engine.connect()
        username = session.get('username')
        app.logger.critical(username)
        select_st = select([prof]).where(prof.c.username == username)
        query = conn.execute(select_st)
        for row in query:
            role = row['role']
            partner = row['partner']
            session['svc_a'] = row['svc_a']
            session['svc_b'] = row['svc_b']
            session['svc_c'] = row['svc_c']
            session['svc_d'] = row['svc_d']
            session['svc_e'] = row['svc_e']
            session['svc_e'] = row['svc_f']
            app.logger.critical(row)
        session['role'] = role
        session['partner'] = partner
        if  role == 'admin_role':
            return f(*args, **kwargs)
        elif role == 'operator_role':
            return redirect(url_for('partner', next=request.url))
        else :
            return redirect(url_for('home', next=request.url))
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if  session['role'] == 'admin_role':
            return f(*args, **kwargs)
        else :
            return redirect(url_for('home', next=request.url))
            #return render_template('login.html')
    return decorated_function

def partnerA_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        role = session.get('roles')
        partner = session.get ('partner')
        if role == 'operator' and partner == 'Accenture' or role =='admin':
            return f(*args, **kwargs)
        else :
            return redirect(url_for('home', next=request.url))
    return decorated_function

def partnerB_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        role = session.get('roles')
        partner = session.get ('partner')
        if role == 'operator' and partner == 'CapGemini' or role =='admin':
            return f(*args, **kwargs)
        else :
            return redirect(url_for('home', next=request.url))
    return decorated_function

#### tainersUp application routes #####
@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        #return dkinfo()
        return "Please logout  <a href='/logout'>Logout</a>"

@app.route('/login', methods=['POST'])
def do_admin_login():
    POST_USERNAME = str(request.form['username'])
    POST_PASSWORD = str(request.form['password'])
    conn = engine.connect()
    select_st = select([act]).where(act.c.username == POST_USERNAME)
    query = conn.execute(select_st)
    for row in query:
        username = row['username']
        password = row['password']
        firstname = row['firstname']
        lastname = row['lastname']
        creationdate = row['creationdate']
        pwdreset = row['pwdreset']
    result = bcrypt.check_password_hash(password, POST_PASSWORD) # returns True
    if result:
        session['logged_in'] = True
        session['username'] = username
        user1 = session.get('username')
        app.logger.critical(user1)
    else:
        flash('wrong password!')
    return dkinfo()

@app.route("/dockerinfo")
@auth_required
def dkinfo():
    if session.get('logged_in'):
        output = subprocess.check_output('docker info | tee templates/resultableInfo.txt', shell=True,stderr=subprocess.STDOUT,)
        output = "<h3>cmd = <b>docker info</b></h3>" + output
        output = "<h2>Docker Installation Cfg</h2>" + output
        output = "{% extends \"results.html\" %}{% block body %}<pre>" + output
        output = output + "</pre> {% endblock %}}"
        f = open('templates/resultableInfo.html', 'w')
        f.write(output)
        f.close()
        return render_template('resultableInfo.html')
    else:
        return render_template('login.html')
#
# start of partner page routes
#
@app.route("/partner")
def partner():
    if session.get('logged_in'):
        conn = engine.connect()
        username = session.get('username')
        partner = session.get('partner')
        app.logger.critical(partner)
        #select partner info
        select_st = select([prtnr]).where(prtnr.c.partner == partner)
        query = conn.execute(select_st)
        for row in query:
            partner1 = row['partnername']
            app.logger.critical(partner1)
        #select username info
        select_st = select([act]).where(act.c.username == username)
        query = conn.execute(select_st)
        for row in query:
            firstname = row['firstname']
            app.logger.critical(firstname)
            lastname = row['lastname']
            app.logger.critical(lastname)

        partner_list = []
        app.logger.critical(partner1)
        s = select([issu]).where(issu.c.partner == partner1)
        s2 = conn.execute(s)

        partner_dict = {}
        for row in s2:
            issue_id = (row['id'])
            partner_dict.update({'issue_id':issue_id})
            servicename = str(row['service'])
            partner_dict.update({'service':servicename})
            issueDescription = str(row['issueDescription'])
            partner_dict.update({'issueDescription':issueDescription})
            updates = str(row['updates'])
            partner_dict.update({'Actions':updates})
            issueRequestor = str(row['issueRequestor'])
            partner_dict.update({'issueRequestor':issueRequestor})
            assignment = str(row['assignment'])
            partner_dict.update({'date':assignment})
            resolved = str(row['resolved'])
            partner_dict.update({'resolved':resolved})
            app.logger.critical(partner_dict)
            app.logger.critical(issue_id)
            if issue_id > 0:
                partner_list.append(dict(partner_dict))
                app.logger.critical(partner_list)

        return render_template('partnerissues.html', partner = partner1, username = username, \
        firstname = firstname, lastname = lastname, partner_list = partner_list)
    else:
        return render_template('login.html')

@app.route('/issuepartnerdelete', methods=['POST'])
def issuepartnerdelete():
    if session.get('logged_in'):
        POST_ISSUE_ID = (request.form['issue_id'])
        app.logger.critical(POST_ISSUE_ID)
        try:
            conn = engine.connect()
            issu1 = issu.delete().where(issu.c.id == POST_ISSUE_ID)
            issu2 = conn.execute(issu1)
            return redirect(url_for('partner'))
        except subprocess.CalledProcessError as e:
            return render_template("500.html", error = str(e))
    else:
        return render_template('login.html')

@app.route('/issuepartneredit', methods=['POST'])
def issuepartneredit():
    if session.get('logged_in'):
        POST_ISSUE_ID = (request.form['issue_id'])
        app.logger.critical(POST_ISSUE_ID)
        try:
            conn = engine.connect()
            issue1 = select([issu]).where(issu.c.id == POST_ISSUE_ID)
            issue2 = conn.execute(issue1)
            issue_edit_dict = {}
            for row in issue2:
                issue_id = (row['id'])
                issue_edit_dict.update({'issue_id':issue_id})
                servicename = str(row['service'])
                issue_edit_dict.update({'service':servicename})
                issueDescription = str(row['issueDescription'])
                issue_edit_dict.update({'issueDescription':issueDescription})
                updates = str(row['updates'])
                issue_edit_dict.update({'Actions':updates})
                issueRequestor = str(row['issueRequestor'])
                issue_edit_dict.update({'issueRequestor':issueRequestor})
                assignment = str(row['assignment'])
                issue_edit_dict.update({'date':assignment})
                resolved = str(row['resolved'])
                issue_edit_dict.update({'resolved':resolved})
                app.logger.critical(issue_edit_dict)
                app.logger.critical(issue_id)
            return render_template('issuedit.html', issue_edit_dict = issue_edit_dict)
        except subprocess.CalledProcessError as e:
            return render_template("500.html", error = str(e))
    else:
        return render_template('login.html')

@app.route('/issuepartnercancel', methods=['POST'])
def issuepartnercancel():
    if session.get('logged_in'):
        try:
            return redirect(url_for('partner'))
        except subprocess.CalledProcessError as e:
            return render_template("500.html", error = str(e))
        else:
            return render_template('login.html')

@app.route('/issuepartnersave', methods=['POST'])
def issuepartnersave():
    if session.get('logged_in'):
        POST_ISSUE_ID = str(request.form['issue_id'])
        POST_ISSUE_DESCRIPTION = str(request.form['issueDescriptions'])
        POST_ISSUE_ACTION = str(request.form['issueActions'])
        POST_ISSUE_RESOLVED = str(request.form['resolved'])
        if POST_ISSUE_RESOLVED == 'Yes':
            resolved_int = 1
        else:
            resolved_int = 0
        app.logger.critical(POST_ISSUE_ID)
        app.logger.critical(POST_ISSUE_DESCRIPTION)
        app.logger.critical(POST_ISSUE_ACTION)
        app.logger.critical(POST_ISSUE_RESOLVED)
        app.logger.critical(resolved_int)
        try:
            conn = engine.connect()
            issue1 = update(issu).where(issu.c.id == POST_ISSUE_ID).values( \
                            issueDescription = POST_ISSUE_DESCRIPTION,\
                            updates = POST_ISSUE_ACTION,\
                            resolved = resolved_int\
                        )
            issue2 = conn.execute(issue1)
            return redirect(url_for('partner'))
        except subprocess.CalledProcessError as e:
            return render_template("500.html", error = str(e))
    else:
        return render_template('login.html')

@app.route('/issuepartnercreate', methods=['POST'])
def issuepartnercreate():
    if session.get('logged_in'):
        try:
            # Get session information, partnername & full name
            conn = engine.connect()
            username = session.get('username')
            partner = session.get('partner')
            app.logger.critical(partner)
            #select partner info
            select_st = select([prtnr]).where(prtnr.c.partner == partner)
            query = conn.execute(select_st)
            for row in query:
                partner1 = row['partnername']
                app.logger.critical(partner1)
            #select username info
            select_st = select([act]).where(act.c.username == username)
            query = conn.execute(select_st)
            for row in query:
                firstname = row['firstname']
                app.logger.critical(firstname)
                lastname = row['lastname']
                app.logger.critical(lastname)

            # select services defined in profile that are enabled
            service_enabled_list = []
            svc1 = select([prof]).where(prof.c.username == username)
            svc2 = conn.execute(svc1)
            for row in svc2:
                svcvalue = (row['svc_a'])
                if svcvalue == 1:
                    service_enabled_list.append('svc_a')
                svcvalue = (row['svc_b'])
                if svcvalue == 1:
                    service_enabled_list.append('svc_b')
                svcvalue = (row['svc_c'])
                if svcvalue == 1:
                    service_enabled_list.append('svc_c')
                svcvalue = (row['svc_d'])
                if svcvalue == 1:
                    service_enabled_list.append('svc_d')
                svcvalue = (row['svc_e'])
                if svcvalue == 1:
                    service_enabled_list.append('svc_e')
                svcvalue = (row['svc_f'])
                if svcvalue == 1:
                    service_enabled_list.append('svc_f')
                app.logger.critical(service_enabled_list)

            #Generate service name dictionary
            svcname_dict = {}
            svc1 = select([svcs]).where(svcs.c.service == 'svc_a')
            svc2 = conn.execute(svc1)
            for row in svc2:
                svcname = str(row['servicename'])
                svcname_dict.update({'svc_a':svcname})
            svc1 = select([svcs]).where(svcs.c.service == 'svc_b')
            svc2 = conn.execute(svc1)
            for row in svc2:
                svcname = str(row['servicename'])
                svcname_dict.update({'svc_b':svcname})
            svc1 = select([svcs]).where(svcs.c.service == 'svc_c')
            svc2 = conn.execute(svc1)
            for row in svc2:
                svcname = str(row['servicename'])
                svcname_dict.update({'svc_c':svcname})
            svc1 = select([svcs]).where(svcs.c.service == 'svc_d')
            svc2 = conn.execute(svc1)
            for row in svc2:
                svcname = str(row['servicename'])
                svcname_dict.update({'svc_d':svcname})
            svc1 = select([svcs]).where(svcs.c.service == 'svc_e')
            svc2 = conn.execute(svc1)
            for row in svc2:
                svcname = str(row['servicename'])
                svcname_dict.update({'svc_e':svcname})
            svc1 = select([svcs]).where(svcs.c.service == 'svc_f')
            svc2 = conn.execute(svc1)
            for row in svc2:
                svcname = str(row['servicename'])
                svcname_dict.update({'svc_f':svcname})

            app.logger.critical(svcname_dict)

            #Query svcname_dict for all enabled services and create service dropdown dictionary
            service_dict = {}
            stack1 = {}
            for svc in service_enabled_list:
                svcdrop = svcname_dict.get(svc)
                stack1.update({svcdrop:svcdrop})
            service_dict = [stack1]
            app.logger.critical(service_dict)

            return render_template('issuecreate.html', username = username, partner = partner1, \
            firstname = firstname, lastname = lastname, service_dict = service_dict )
        except subprocess.CalledProcessError as e:
            return render_template("500.html", error = str(e))
    else:
        return render_template('login.html')

@app.route('/issuecreatesave', methods=['POST'])
def issuecreatesave():
    if session.get('logged_in'):
        POST_SERVICE = str(request.form['service'])
        POST_ISSUEREQUESTOR = str(request.form['issueRequestor'])
        POST_PARTNER = str(request.form['partner'])
        POST_ISSUEDESCRIPTIONS = str(request.form['issueDescriptions'])
        POST_ISSUEACTIONS = str(request.form['issueActions'])
        POST_RESOLVED = str(request.form['resolved'])
        app.logger.critical(POST_SERVICE)
        app.logger.critical(POST_ISSUEREQUESTOR)
        app.logger.critical(POST_PARTNER)
        app.logger.critical(POST_ISSUEDESCRIPTIONS)
        app.logger.critical(POST_ISSUEACTIONS)
        app.logger.critical(POST_RESOLVED)
        if POST_RESOLVED == 'No':
            resolved_int = 0
        else:
            rosolved_int = 1

        try:
            now = datetime.datetime.now()
            conn = engine.connect()
            svc = conn.execute(issu.insert(),[{'partner':POST_PARTNER,'service':POST_SERVICE,'updates':POST_ISSUEACTIONS ,\
            'issueDescription':POST_ISSUEDESCRIPTIONS,'issueRequestor':POST_ISSUEREQUESTOR,'assignment': now.strftime("%Y-%m-%d %H:%M"),'resolved':resolved_int}])
            #svc1 = conn.execute(svc)
            return redirect(url_for('partner'))
        except subprocess.CalledProcessError as e:
            return render_template("500.html", error = str(e))
    else:
        return render_template('login.html')

# start of admin page routes
@app.route("/useradmin")
@admin_required
def useradmin():
    if session.get('logged_in'):
        conn = engine.connect()
        partner = session.get('partner')
        app.logger.critical(partner)
        select_st = select([prtnr]).where(prtnr.c.partner == partner)
        query = conn.execute(select_st)
        for row in query:
            partner1 = row['partnername']
        # select Services
        s = select([svcs])
        s1 = conn.execute(s)
        stack = {}
        for row in s1:
            #app.logger.critical(row)
            service = str(row['service'])
            servicename = str(row['servicename'])
            stack.update({service:servicename})
            #app.logger.critical(stack)
        service_dict = [stack]
            # select Partners
        s1 = select([prtnr])
        s2 = conn.execute(s1)
        stack1 = {}
        for row in s2:
            partner = str(row['partner'])
            partnername = str(row['partnername'])
            stack1.update({partner:partnername})
            app.logger.critical(stack1)
        partner_dict = [stack1]
            # select roles
        s1 = select([rolls])
        s2 = conn.execute(s1)
        stack1 = {}
        for row in s2:
            role = str(row['role'])
            rolename = str(row['rolename'])
            stack1.update({role:rolename})
            app.logger.critical(stack1)
        role_dict = [stack1]
            # select Users
        s1 = select([act])
        s2 = conn.execute(s1)
        list1 = []
        user_rows = 0
        for row in s2:
            username = str(row['username'])
            app.logger.critical(username)
            list1.append(username)
            firstname = str(row['firstname'])
            list1.append(firstname)
            app.logger.critical(firstname)
            lastname = str(row['lastname'])
            list1.append(lastname)
            app.logger.critical(lastname)
            #stack1.update({'user':username,'first':firstname,'last':lastname})
            app.logger.critical(list1)
            user_rows += 1
        user_list = (list1)
        app.logger.critical(user_list)
            # select Profiles
        s3 = select([prof])
        s4 = conn.execute(s3)
        list2 = []
        prof_rows = 0
        for row in s4:
            username_prof = str(row['username'])
            list2.append(username_prof)
            app.logger.critical(username_prof)
            role_prof = str(row['role'])
            list2.append(role_prof)
            app.logger.critical(role_prof)
            partner_prof = str(row['partner'])
            list2.append(partner_prof)
            app.logger.critical(partner_prof)
            svc_a_prof = (row['svc_a'])
            list2.append(svc_a_prof)
            app.logger.critical(svc_a_prof)
            svc_b_prof = str(row['svc_b'])
            list2.append(svc_b_prof)
            app.logger.critical(svc_b_prof)
            svc_c_prof = str(row['svc_c'])
            list2.append(svc_c_prof)
            app.logger.critical(svc_c_prof)
            svc_d_prof = str(row['svc_d'])
            list2.append(svc_d_prof)
            app.logger.critical(svc_d_prof)
            svc_e_prof = str(row['svc_e'])
            list2.append(svc_e_prof)
            app.logger.critical(svc_e_prof)
            svc_f_prof = str(row['svc_f'])
            list2.append(svc_f_prof)
            app.logger.critical(svc_f_prof)
            prof_rows += 1
        prof_list = (list2)
        app.logger.critical(prof_list)
        return render_template('useradmin.html', partner = partner1, service_dict = service_dict, \
        partner_dict = partner_dict, role_dict = role_dict, user_list = user_list, prof_list = prof_list,
        prof_rows = prof_rows, user_rows = user_rows)
    else:
        return render_template('login.html')

@app.route('/adminsvcedit', methods=['POST'])
def adminsvcedit():
    if session.get('logged_in'):
        POST_SVCNAME = str(request.form['svceditname'])
        app.logger.critical(POST_SVCNAME)
        try:
            conn = engine.connect()
            svc = select([svcs]).where(svcs.c.servicename == POST_SVCNAME)
            svc1 = conn.execute(svc)
            stack = {}
            for row in svc1:
                #app.logger.critical(row)
                service = str(row['service'])
                servicename = str(row['servicename'])
                stack.update({service:servicename})
                #app.logger.critical(stack)
            service_edit_dict = [stack]
            return render_template('svcedit.html', service_edit_dict = service_edit_dict)
        except subprocess.CalledProcessError as e:
            return render_template("500.html", error = str(e))
    else:
        return render_template('login.html')

@app.route('/adminsvcsave', methods=['POST'])
def adminsvcsave():
    if session.get('logged_in'):
        POST_SVC = str(request.form['svc'])
        POST_SVCNAME = str(request.form['svcname'])
        app.logger.critical(POST_SVC)
        app.logger.critical(POST_SVCNAME)
        try:
            conn = engine.connect()
            svc = update(svcs).where(svcs.c.service == POST_SVC).values(servicename = POST_SVCNAME)
            svc1 = conn.execute(svc)
            return redirect(url_for('useradmin'))
        except subprocess.CalledProcessError as e:
            return render_template("500.html", error = str(e))
    else:
        return render_template('login.html')

@app.route('/adminprtnrsave', methods=['POST'])
def adminprtnrsave():
    if session.get('logged_in'):
        POST_PRTNR = str(request.form['prtnr'])
        POST_PRTNRNAME = str(request.form['prtnrname'])
        app.logger.critical(POST_PRTNR)
        app.logger.critical(POST_PRTNRNAME)
        try:
            conn = engine.connect()
            prtnr1 = update(prtnr).where(prtnr.c.partner == POST_PRTNR).values(partnername = POST_PRTNRNAME)
            prtnr2 = conn.execute(prtnr1)
            return redirect(url_for('useradmin'))
        except subprocess.CalledProcessError as e:
            return render_template("500.html", error = str(e))
    else:
        return render_template('login.html')

@app.route('/adminrolesave', methods=['POST'])
def adminrolesave():
    if session.get('logged_in'):
        POST_ROLE = str(request.form['role'])
        POST_ROLENAME = str(request.form['rolename'])
        app.logger.critical(POST_ROLE)
        app.logger.critical(POST_ROLENAME)
        try:
            conn = engine.connect()
            role1 = update(rolls).where(rolls.c.role == POST_ROLE).values(rolename = POST_ROLENAME)
            role2 = conn.execute(role1)
            return redirect(url_for('useradmin'))
        except subprocess.CalledProcessError as e:
            return render_template("500.html", error = str(e))
    else:
        return render_template('login.html')

@app.route('/adminprtnredit', methods=['POST'])
def adminprtnredit():
    if session.get('logged_in'):
        POST_PRTNRNAME = str(request.form['prtnreditname'])
        app.logger.critical(POST_PRTNRNAME)
        try:
            conn = engine.connect()
            ptnr = select([prtnr]).where(prtnr.c.partnername == POST_PRTNRNAME)
            prtnr1 = conn.execute(ptnr)
            stack = {}
            for row in prtnr1:
                #app.logger.critical(row)
                partner = str(row['partner'])
                partnername = str(row['partnername'])
                stack.update({partner:partnername})
                #app.logger.critical(stack)
            partner_edit_dict = [stack]
            return render_template('prtnredit.html', partner_edit_dict = partner_edit_dict)
        except subprocess.CalledProcessError as e:
            return render_template("500.html", error = str(e))
    else:
        return render_template('login.html')

@app.route('/adminroleedit', methods=['POST'])
def adminroleedit():
    if session.get('logged_in'):
        POST_ROLENAME = str(request.form['roleeditname'])
        app.logger.critical(POST_ROLENAME)
        try:
            conn = engine.connect()
            role = select([rolls]).where(rolls.c.rolename == POST_ROLENAME)
            role1 = conn.execute(role)
            stack = {}
            for row in role1:
                #app.logger.critical(row)
                role = str(row['role'])
                rolename = str(row['rolename'])
                stack.update({role:rolename})
                #app.logger.critical(stack)
            role_edit_dict = [stack]
            return render_template('roleedit.html', role_edit_dict = role_edit_dict)
        except subprocess.CalledProcessError as e:
            return render_template("500.html", error = str(e))
    else:
        return render_template('login.html')

@app.route('/adminprofedit', methods=['POST'])
def adminprofedit():
    if session.get('logged_in'):
        POST_USERNAME = str(request.form['username'])
        app.logger.critical(POST_USERNAME)
        try:
            conn = engine.connect()
            prof1 = select([prof]).where(prof.c.username == POST_USERNAME)
            prof2 = conn.execute(prof1)
            list2 = []
            prof_rows = 0
            for row in prof2:
                username_prof = str(row['username'])
                list2.append(username_prof)
                app.logger.critical(username_prof)
                role_prof = str(row['role'])
                list2.append(role_prof)
                app.logger.critical(role_prof)
                partner_prof = str(row['partner'])
                list2.append(partner_prof)
                app.logger.critical(partner_prof)
                svc_a_prof = (row['svc_a'])
                list2.append(svc_a_prof)
                app.logger.critical(svc_a_prof)
                svc_b_prof = str(row['svc_b'])
                list2.append(svc_b_prof)
                app.logger.critical(svc_b_prof)
                svc_c_prof = str(row['svc_c'])
                list2.append(svc_c_prof)
                app.logger.critical(svc_c_prof)
                svc_d_prof = str(row['svc_d'])
                list2.append(svc_d_prof)
                app.logger.critical(svc_d_prof)
                svc_e_prof = str(row['svc_e'])
                list2.append(svc_e_prof)
                app.logger.critical(svc_e_prof)
                svc_f_prof = str(row['svc_f'])
                list2.append(svc_f_prof)
                app.logger.critical(svc_f_prof)
                prof_rows += 1
            prof_list = (list2)
            app.logger.critical(prof_list)
            app.logger.critical(role_prof)
            rolename_list = []
            role1 = select([rolls]).where(rolls.c.role == role_prof)
            role2 = conn.execute(role1)
            for row in role2:
                rolename = str(row['rolename'])
                rolename_list.append(rolename)
            prtnrname_list = []
            prtnr1 = select([prtnr]).where(prtnr.c.partner == partner_prof)
            prtnr2 = conn.execute(prtnr1)
            for row in prtnr2:
                prtnrname = str(row['partnername'])
                prtnrname_list.append(prtnrname)
            svcname_list = []
            svc1 = select([svcs]).where(svcs.c.service == 'svc_a')
            svc2 = conn.execute(svc1)
            for row in svc2:
                svcname = str(row['servicename'])
                svcname_list.append(svcname)
            svc1 = select([svcs]).where(svcs.c.service == 'svc_b')
            svc2 = conn.execute(svc1)
            for row in svc2:
                svcname = str(row['servicename'])
                svcname_list.append(svcname)
            svc1 = select([svcs]).where(svcs.c.service == 'svc_c')
            svc2 = conn.execute(svc1)
            for row in svc2:
                svcname = str(row['servicename'])
                svcname_list.append(svcname)
            svc1 = select([svcs]).where(svcs.c.service == 'svc_d')
            svc2 = conn.execute(svc1)
            for row in svc2:
                svcname = str(row['servicename'])
                svcname_list.append(svcname)
            svc1 = select([svcs]).where(svcs.c.service == 'svc_e')
            svc2 = conn.execute(svc1)
            for row in svc2:
                svcname = str(row['servicename'])
                svcname_list.append(svcname)
            svc1 = select([svcs]).where(svcs.c.service == 'svc_f')
            svc2 = conn.execute(svc1)
            for row in svc2:
                svcname = str(row['servicename'])
                svcname_list.append(svcname)

                # select Partners
            s1 = select([prtnr])
            s2 = conn.execute(s1)
            stack1 = {}
            for row in s2:
                partner = str(row['partner'])
                partnername = str(row['partnername'])
                stack1.update({partner:partnername})
                app.logger.critical(stack1)
            partner_dict = [stack1]
                # select roles
            s1 = select([rolls])
            s2 = conn.execute(s1)
            stack1 = {}
            for row in s2:
                role = str(row['role'])
                rolename = str(row['rolename'])
                stack1.update({role:rolename})
                app.logger.critical(stack1)
            role_dict = [stack1]
            return render_template('profileedit.html', prof_list = prof_list,username_prof = username_prof, \
            rolename_list = rolename_list, prtnrname_list = prtnrname_list, svcname_list = svcname_list, \
            partner_dict = partner_dict, role_dict = role_dict)
        except subprocess.CalledProcessError as e:
            return render_template("500.html", error = str(e))
    else:
        return render_template('login.html')

@app.route('/adminprofilesave', methods=['POST'])
def adminprofilesave():
    if session.get('logged_in'):
        POST_USERNAME = str(request.form['profileusername'])
        POST_ROLE = str(request.form['role'])
        POST_PARTNER = str(request.form['partner'])
        POST_SVC_A = str(request.form['svc_a'])
        POST_SVC_B = str(request.form['svc_b'])
        POST_SVC_C = str(request.form['svc_c'])
        POST_SVC_D = str(request.form['svc_d'])
        POST_SVC_E = str(request.form['svc_e'])
        POST_SVC_F = str(request.form['svc_f'])

        app.logger.critical(POST_USERNAME)
        app.logger.critical(POST_ROLE)
        app.logger.critical(POST_PARTNER)
        app.logger.critical(POST_SVC_A)
        app.logger.critical(POST_SVC_B)
        app.logger.critical(POST_SVC_C)
        app.logger.critical(POST_SVC_D)
        app.logger.critical(POST_SVC_E)
        app.logger.critical(POST_SVC_F)
        try:
            conn = engine.connect()
            #prof1 = update(prof).where(prof.c.username == 'buser').values(role = 'admin_role')
            prof1 = update(prof).where(prof.c.username == POST_USERNAME).values(role = POST_ROLE,\
            partner = POST_PARTNER, svc_a = POST_SVC_A, svc_b = POST_SVC_B, svc_c = POST_SVC_C,\
            svc_d = POST_SVC_D, svc_e = POST_SVC_E, svc_f = POST_SVC_F )
            prof2 = conn.execute(prof1)
            return redirect(url_for('useradmin'))
        except subprocess.CalledProcessError as e:
            return render_template("500.html", error = str(e))
    else:
        return render_template('login.html')

@app.route('/admincancel', methods=['POST'])
def admincancel():
    if session.get('logged_in'):
        try:
            return redirect(url_for('useradmin'))
        except subprocess.CalledProcessError as e:
            return render_template("500.html", error = str(e))
        else:
            return render_template('login.html')

@app.route('/adminprofdelete', methods=['POST'])
def adminprofdelete():
    if session.get('logged_in'):
        POST_USERNAME = str(request.form['username'])
        app.logger.critical(POST_USERNAME)
        try:
            conn = engine.connect()
            prof1 = prof.delete().where(prof.c.username == POST_USERNAME)
            prof2 = conn.execute(prof1)
            return redirect(url_for('useradmin'))
        except subprocess.CalledProcessError as e:
            return render_template("500.html", error = str(e))
    else:
        return render_template('login.html')

@app.route('/adminusercreate', methods=['POST'])
def adminusercreate():
    if session.get('logged_in'):
        try:
            return render_template('usercreate.html')
        except subprocess.CalledProcessError as e:
            return render_template("500.html", error = str(e))
    else:
        return render_template('login.html')

@app.route('/adminusersave', methods=['POST'])
def adminusersave():
    if session.get('logged_in'):
        POST_USERNAME = str(request.form['username'])
        POST_PASSWORD = str(request.form['password'])
        POST_FIRSTNAME = str(request.form['firstname'])
        POST_LASTNAME = str(request.form['lastname'])
        app.logger.critical(POST_USERNAME)
        app.logger.critical(POST_PASSWORD)
        app.logger.critical(POST_FIRSTNAME)
        app.logger.critical(POST_LASTNAME)
        try:
            now = datetime.datetime.now()
            password = bcrypt.generate_password_hash(POST_PASSWORD)
            conn = engine.connect()
            conn.execute(act.insert(),[
            {'username':POST_USERNAME,'password':password,'firstname':POST_FIRSTNAME,'lastname':POST_LASTNAME,\
            'creationdate': now.strftime("%Y-%m-%d %H:%M"),'pwdreset':'0'}])
            return redirect(url_for('useradmin'))
        except subprocess.CalledProcessError as e:
            return render_template("500.html", error = str(e))
    else:
        return render_template('login.html')

@app.route('/adminuserdelete', methods=['POST'])
def adminuserdelete():
    if session.get('logged_in'):
        POST_USERNAME = str(request.form['username'])
        app.logger.critical(POST_USERNAME)
        try:
            conn = engine.connect()
            act1 = act.delete().where(act.c.username == POST_USERNAME)
            act2 = conn.execute(act1)
            return redirect(url_for('useradmin'))
        except subprocess.CalledProcessError as e:
            return render_template("500.html", error = str(e))
    else:
        return render_template('login.html')

@app.route('/adminuseredit', methods=['POST'])
def adminuseredit():
    if session.get('logged_in'):
        POST_USERNAME = str(request.form['username'])
        app.logger.critical(POST_USERNAME)
        try:
            conn = engine.connect()
            act1 = select([act]).where(act.c.username == POST_USERNAME)
            act2 = conn.execute(act1)
            list2 = []
            for row in act2:
                username_act = str(row['username'])
                list2.append(username_act)
                app.logger.critical(username_act)
                firstname_act = str(row['firstname'])
                list2.append(firstname_act)
                app.logger.critical(firstname_act)
                lastname_act = str(row['lastname'])
                list2.append(lastname_act)
                app.logger.critical(lastname_act)
            act_list = (list2)
            app.logger.critical(act_list)
            return render_template('useredit.html', act_list = act_list)
        except subprocess.CalledProcessError as e:
            return render_template("500.html", error = str(e))
    else:
        return render_template('login.html')

@app.route('/adminusereditsave', methods=['POST'])
def adminusereditsave():
    if session.get('logged_in'):
        POST_USERNAME = str(request.form['actusername'])
        POST_FIRSTNAME = str(request.form['actfirstname'])
        POST_LASTNAME = str(request.form['actlastname'])
        app.logger.critical(POST_USERNAME)
        app.logger.critical(POST_FIRSTNAME)
        app.logger.critical(POST_LASTNAME)
        try:
            conn = engine.connect()
            act1 = update(act).where(act.c.username == POST_USERNAME).values(firstname = POST_FIRSTNAME,\
            lastname = POST_LASTNAME)
            conn.execute(act1)
            return redirect(url_for('useradmin'))
        except subprocess.CalledProcessError as e:
            return render_template("500.html", error = str(e))
    else:
        return render_template('login.html')

@app.route('/adminusereditpwd', methods=['POST'])
def adminusereditpwd():
    if session.get('logged_in'):
        POST_USERNAME = str(request.form['username'])
        app.logger.critical(POST_USERNAME)
        pwdusername = POST_USERNAME
        try:
            return render_template('pwdedit.html', pwdusername = pwdusername)
        except subprocess.CalledProcessError as e:
            return render_template("500.html", error = str(e))
    else:
        return render_template('login.html')

@app.route('/adminuserpwdsave', methods=['POST'])
def adminuserpwdsave():
    if session.get('logged_in'):
        POST_USERNAME = str(request.form['username'])
        POST_PASSWORD = str(request.form['pwd2'])
        app.logger.critical(POST_USERNAME)
        #app.logger.critical(POST_PASSWORD)
        password = bcrypt.generate_password_hash(POST_PASSWORD)
        try:
            conn = engine.connect()
            act1 = update(act).where(act.c.username == POST_USERNAME).values(password = password)
            act2 = conn.execute(act1)
            return redirect(url_for('useradmin'))
        except subprocess.CalledProcessError as e:
            return render_template("500.html", error = str(e))
    else:
        return render_template('login.html')

@app.route('/adminprofcreate', methods=['POST'])
def adminprofcreate():
    if session.get('logged_in'):

        try:
            conn = engine.connect()
            # select all user usernames
            act1 = select([act])
            act2 = conn.execute(act1)
            list3 = []
            for row in act2:
                username_act = str(row['username'])
                list3.append(username_act)
            act_list = (list3)
            # select all profile usernames
            prof1 = select([prof])
            prof2 = conn.execute(prof1)
            list2 = []
            for row in prof2:
                username_prof = str(row['username'])
                list2.append(username_prof)
            prof_list = (list2)
            #compare act_list to Prof_list and create potential username dropdown list
            userdrop_list = [item for item in act_list if item not in prof_list]
            app.logger.critical(userdrop_list)
            stack1 = {}
            for username_item in userdrop_list:
                stack1.update({username_item:username_item})
            #i = iter(userdrop_list)
            #user_dict = dict(izip(i, i))
            #user_dict = dict(itertools.izip_longest(*[iter(l)] * 2, fillvalue=""))
            user_dict = [stack1]
            app.logger.critical(user_dict)


            rolename_list = []
            role1 = select([rolls]).where(rolls.c.role)
            role2 = conn.execute(role1)
            for row in role2:
                rolename = str(row['rolename'])
                rolename_list.append(rolename)

            prtnrname_list = []
            prtnr1 = select([prtnr]).where(prtnr.c.partner)
            prtnr2 = conn.execute(prtnr1)
            for row in prtnr2:
                prtnrname = str(row['partnername'])
                prtnrname_list.append(prtnrname)

            svcname_list = []
            svc1 = select([svcs]).where(svcs.c.service == 'svc_a')
            svc2 = conn.execute(svc1)
            for row in svc2:
                svcname = str(row['servicename'])
                svcname_list.append(svcname)
            svc1 = select([svcs]).where(svcs.c.service == 'svc_b')
            svc2 = conn.execute(svc1)
            for row in svc2:
                svcname = str(row['servicename'])
                svcname_list.append(svcname)
            svc1 = select([svcs]).where(svcs.c.service == 'svc_c')
            svc2 = conn.execute(svc1)
            for row in svc2:
                svcname = str(row['servicename'])
                svcname_list.append(svcname)
            svc1 = select([svcs]).where(svcs.c.service == 'svc_d')
            svc2 = conn.execute(svc1)
            for row in svc2:
                svcname = str(row['servicename'])
                svcname_list.append(svcname)
            svc1 = select([svcs]).where(svcs.c.service == 'svc_e')
            svc2 = conn.execute(svc1)
            for row in svc2:
                svcname = str(row['servicename'])
                svcname_list.append(svcname)
            svc1 = select([svcs]).where(svcs.c.service == 'svc_f')
            svc2 = conn.execute(svc1)
            for row in svc2:
                svcname = str(row['servicename'])
                svcname_list.append(svcname)

                # select Partners
            s1 = select([prtnr])
            s2 = conn.execute(s1)
            stack1 = {}
            for row in s2:
                partner = str(row['partner'])
                partnername = str(row['partnername'])
                stack1.update({partner:partnername})
                app.logger.critical(stack1)
            partner_dict = [stack1]
                # select roles
            s1 = select([rolls])
            s2 = conn.execute(s1)
            stack1 = {}
            for row in s2:
                role = str(row['role'])
                rolename = str(row['rolename'])
                stack1.update({role:rolename})
                app.logger.critical(stack1)
            role_dict = [stack1]
            #return redirect(url_for('useradmin'))
            return render_template('profilecreate.html', user_dict = user_dict, svcname_list = svcname_list, \
            role_dict = role_dict, partner_dict = partner_dict, )
        except subprocess.CalledProcessError as e:
            return render_template("500.html", error = str(e))
    else:
        return render_template('login.html')

@app.route('/adminprofsavenew', methods=['POST'])
def adminprofsavenew():
    if session.get('logged_in'):
        POST_USERNAME = str(request.form['username'])
        POST_ROLE = str(request.form['role'])
        POST_PARTNER = str(request.form['partner'])
        POST_SVC_A = str(request.form['svc_a'])
        POST_SVC_B = str(request.form['svc_b'])
        POST_SVC_C = str(request.form['svc_c'])
        POST_SVC_D = str(request.form['svc_d'])
        POST_SVC_E = str(request.form['svc_e'])
        POST_SVC_F = str(request.form['svc_f'])
        app.logger.critical(POST_USERNAME)
        app.logger.critical(POST_ROLE)
        app.logger.critical(POST_PARTNER)
        app.logger.critical(POST_SVC_A)
        app.logger.critical(POST_SVC_B)
        app.logger.critical(POST_SVC_C)
        app.logger.critical(POST_SVC_D)
        app.logger.critical(POST_SVC_E)
        app.logger.critical(POST_SVC_F)
        try:
            conn = engine.connect()
            conn.execute(prof.insert(),[
            {'username':POST_USERNAME,'role':POST_ROLE,'partner':POST_PARTNER,'svc_a':POST_SVC_A,\
            'svc_b': POST_SVC_B,'svc_c': POST_SVC_C, 'svc_d': POST_SVC_D,  'svc_e': POST_SVC_E, 'svc_f': POST_SVC_F }])
            return redirect(url_for('useradmin'))
        except subprocess.CalledProcessError as e:
            return render_template("500.html", error = str(e))
    else:
        return render_template('login.html')

# End of admin routes
# Route that will process the file upload
@app.route('/dockerUpload', methods=['POST'])
def upload():
    # Get the name of the uploaded file
    file = request.files['file']
    # Check if the file is one of the allowed types/extensions
    if file and allowed_file(file.filename):
        # Make the filename safe, remove unsupported chars
        filename = secure_filename(file.filename)
        # Move the file form the temporary folder to
        # the upload folder we setup
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # Redirect the user to the uploaded_file route, which
        # will basicaly show on the browser the uploaded file
        return redirect(url_for('uploaded_file',
                                filename=filename))

@app.route('/dockerUploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

@app.route("/tcpport")
def osport():
    if session.get('logged_in'):
        output = subprocess.check_output('lsof -i -n -P | grep TCP | tee templates/resultableInfo.txt', shell=True,stderr=subprocess.STDOUT,)
        output = "<h3>cmd = <b>lsof -i -n -P | grep TCP</b></h3>" + output
        output = "<h2>OS listening ports</h2>" + output
        output = "{% extends \"results.html\" %}{% block body %}<pre>" + output
        output = output + "</pre> {% endblock %}}"
        f = open('templates/resultableInfo.html', 'w')
        f.write(output)
        f.close()
        return render_template('resultableInfo.html')
    else:
        return render_template('login.html')


@app.route("/dockerlist")
def dklist():
    if session.get('logged_in'):
        output = subprocess.check_output('docker images | tee templates/resultableImageList.txt', shell=True,stderr=subprocess.STDOUT,)
        output = "<h3>cmd = <b>docker images</b></h3>" + output
        output = "<h2>Docker Image List</h2>" + output
        output = "{% extends \"results.html\" %}{% block body %}<pre>" + output
        output = output + "</pre> {% endblock %}}"
        f = open('templates/resultableImageList.html', 'w')
        f.write(output)
        f.close()
        return render_template('resultableImageList.html')
    else:
        return render_template('login.html')

@app.route("/dockercontainer")
def dkcontainer():
    if session.get('logged_in'):
        output = subprocess.check_output('docker ps -a | tee templates/resultableTainerList.txt', shell=True,stderr=subprocess.STDOUT,)
        output = "<h3>cmd = <b>docker ps -a</b></h3>" + output
        output = "<h2>Docker Container List</h2>" + output
        output = "{% extends \"results.html\" %}{% block body %}<pre>" + output
        output = output + "</pre> {% endblock %}}"
        f = open('templates/resultableTainerList.html', 'w')
        f.write(output)
        f.close()
        return render_template('resultableTainerList.html')
    else:
        return render_template('login.html')


@app.route("/dockercmd")
def dkcmd():
    if session.get('logged_in'):
        return render_template('docker_command.html')
    else:
        return render_template('login.html')

@app.route("/docker-composecmd")
def dkcomposecmd():
    if session.get('logged_in'):
        return render_template('docker_compose_command.html')
    else:
        return render_template('login.html')

@app.route("/docker-machinecmd")
def dkmachinecmd():
    if session.get('logged_in'):
        return render_template('docker_machine_command.html')
    else:
        return render_template('login.html')

@app.route("/kubernetescmd")
def kubernetescmd():
    if session.get('logged_in'):
        return render_template('kubernetes_command.html')
    else:
        return render_template('login.html')

@app.route("/dockerBuildCreateRun")
def dkbuildcreaterun():
    if session.get('logged_in'):
        return render_template('docker_buildcreaterun.html')
    else:
        return render_template('login.html')


@app.route("/dockerhousekeeping")
def dkhousekeeping():
    if session.get('logged_in'):
        return render_template('docker_housekeeping.html')
    else:
        return render_template('login.html')

@app.route("/dockerbackups")
def dkbackups():
    if session.get('logged_in'):
        return render_template('docker_backups.html')
    else:
        return render_template('login.html')

@app.route("/dockeraccess")
def dkaccess():
    if session.get('logged_in'):
        return render_template('docker_access.html')
    else:
        return render_template('login.html')

@app.route("/dockervolume")
def dkvolume():
    if session.get('logged_in'):
        return render_template('docker_volume.html')
    else:
        return render_template('login.html')

@app.route("/dockerfilesystem")
def dkUFS():
    if session.get('logged_in'):
        return render_template('UnionFileSystem.html')
    else:
        return render_template('login.html')

@app.route("/containermgmt")
def dkcontainermgmt():
    if session.get('logged_in'):
        return render_template('container_mgmt.html')
    else:
        return render_template('login.html')

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return home()

##############################
### Start of mgmt routes #####
##############################

@app.route('/dockerimagesearch', methods=['POST'])
def dkrimagesearch():
    if session.get('logged_in'):
        POST_IMAGETAG = str(request.form['imagetag'])
        try:
            outputScript = "docker search " + POST_IMAGETAG + " | tee templates/resultableImageSearch.txt"
            output = subprocess.check_output(outputScript, shell=True,stderr=subprocess.STDOUT,)
            output = "<h3>cmd = <b>docker search " + POST_IMAGETAG + "</b></h3>" + output
            output = "<h2>Docker Hub Image Search for " + POST_IMAGETAG + "</h2>" + output
            output = "{% extends \"results.html\" %}{% block body %}<pre>" + output
            output = output + "</pre> {% endblock %}}"
            f = open('templates/resultableImageSearch.html', 'w')
            f.write(output)
            f.close()
            return render_template('resultableImageSearch.html')
        except subprocess.CalledProcessError as e:
            return render_template("500.html", error = str(e))
    else:
        return render_template('login.html')

@app.route('/dockerimagepull', methods=['POST'])
def dkrimagepull():
    if session.get('logged_in'):
        POST_IMAGETAG = str(request.form['imagetag'])
        try:
            outputScript = "docker pull " + POST_IMAGETAG + " | tee templates/resultableImagePull.txt"
            output = subprocess.check_output(outputScript, shell=True,stderr=subprocess.STDOUT,)
            output = "<h3>cmd = <b>docker pull " + POST_IMAGETAG + "</b></h3>" + output
            output = "<h2>Docker Hub Image Pull for " + POST_IMAGETAG + "</h2>" + output
            output = "{% extends \"results.html\" %}{% block body %}<pre>" + output
            output = output + "</pre> {% endblock %}}"
            f = open('templates/resultableImagePull.html', 'w')
            f.write(output)
            f.close()
            return render_template('resultableImagePull.html')
        except subprocess.CalledProcessError as e:
            return render_template("500.html", error = str(e))
    else:
        return render_template('login.html')

@app.route('/dockerimagebuild', methods=['POST'])
def dkrimagebuild():
    if session.get('logged_in'):
        POST_IMAGENAME = str(request.form['imagename'])
        DOCKER_FOLDER = app.config['UPLOAD_FOLDER']
        try:
            outputScript = "docker build -t " + POST_IMAGENAME +" " + DOCKER_FOLDER + " | tee templates/resultableImageBuild.txt"
            output = subprocess.check_output(outputScript, shell=True,stderr=subprocess.STDOUT,)
            output = "<h3>cmd = <b>docker build -t " + POST_IMAGENAME + " " + DOCKER_FOLDER + "</b></h3>" + output
            output = "<h2>Docker Hub Image Build " + POST_IMAGENAME + "</h2>" + output
            output = "{% extends \"results.html\" %}{% block body %}<pre>" + output
            output = output + "</pre> {% endblock %}}"
            f = open('templates/resultableImageBuild.html', 'w')
            f.write(output)
            f.close()
            return render_template('resultableImageBuild.html')
            #return outputScript
        except subprocess.CalledProcessError as e:
            return render_template("500.html", error = str(e))
    else:
        return render_template('login.html')

@app.route('/dockerimagerun', methods=['POST'])
def dkrimagerun():
    if session.get('logged_in'):
        POST_IMAGENAME = str(request.form['imagename'])
        try:
            outputScript = "docker run -d " + POST_IMAGENAME + " | tee templates/resultableImageRun.txt"
            output = subprocess.check_output(outputScript, shell=True,stderr=subprocess.STDOUT,)
            output = "<h3>cmd = <b>docker run -d " + POST_IMAGENAME + "</b></h3>" + output
            output = "<h2>Docker Image Run " + POST_IMAGENAME + "</h2>" + output
            output = "{% extends \"results.html\" %}{% block body %}<pre>" + output
            output = output + "</pre> {% endblock %}}"
            f = open('templates/resultableImageRun.html', 'w')
            f.write(output)
            f.close()
            return render_template('resultableImageRun.html')
            return outputScript
        except subprocess.CalledProcessError as e:
            return render_template("500.html", error = str(e))
    else:
        return render_template('login.html')

@app.route('/dockerimagerunport', methods=['POST'])
def dkrimagerunport():
    if session.get('logged_in'):
        POST_IMAGENAME = str(request.form['imagename'])
        POST_PORT = str(request.form['containerport'])
        DOCKER_FOLDER = app.config['UPLOAD_FOLDER']
        try:
            outputScript = "docker run -d -p " +POST_PORT+ " " + POST_IMAGENAME + " | tee templates/resultableImageRunPort.txt"
            output = subprocess.check_output(outputScript, shell=True,stderr=subprocess.STDOUT,)
            output = "<h3>cmd = <b>docker run -d -p "  +POST_PORT+ " " + POST_IMAGENAME + "</b></h3>" + output
            output = "<h2>Docker Image Run " + POST_IMAGENAME + "</h2>" + output
            output = "{% extends \"results.html\" %}{% block body %}<pre>" + output
            output = output + "</pre> {% endblock %}}"
            f = open('templates/resultableImageRunPort.html', 'w')
            f.write(output)
            f.close()
            return render_template('resultableImageRunPort.html')
            #return outputScript
        except subprocess.CalledProcessError as e:
            return render_template("500.html", error = str(e))
    else:
        return render_template('login.html')

@app.route('/dockerimagedelete', methods=['POST'])
def dkimagedelete():
    if session.get('logged_in'):
        POST_REPOIMAGETAG = str(request.form['repositoryimagetag'])
        try:
            outputScript = "docker rmi -f " + POST_REPOIMAGETAG + " | tee templates/resultableImageDelete.txt"
            output = subprocess.check_output(outputScript, stderr=subprocess.STDOUT, shell=True)
            output = "<h3>cmd = <b>docker rmi -f " + POST_REPOIMAGETAG + "</b></h3>" + output
            output = "<h2>Docker Image Deletion of " + POST_REPOIMAGETAG + "</h2>" + output
            output = "{% extends \"results.html\" %}{% block body %}<pre>" + output
            output = output + "</pre> {% endblock %}}"
            f = open('templates/resultableImageDelete.html', 'w')
            f.write(output)
            f.close()
            return render_template('resultableImageDelete.html')
        except subprocess.CalledProcessError as e:
            return render_template("500.html", error = str(e))

    else:
        return render_template('login.html')

@app.route('/dockerImageDanglingDelete', methods=['POST'])
def dkimagedanglingdelete():
    if session.get('logged_in'):
        try:
            outputScript = "docker rmi $(docker images -q -f dangling=true) | tee templates/resultableImageDangling.txt"
            output = subprocess.check_output(outputScript, shell=True,stderr=subprocess.STDOUT,)
            output = "<h3>cmd = <b>docker rmi $(docker images -q -f dangling=true)</b></h3>" + output
            output = "<h2>Docker Dangling Image Deletion</h2>" + output
            output = "{% extends \"results.html\" %}{% block body %}<pre>" + output
            output = output + "</pre> {% endblock %}}"
            f = open('templates/resultableImageDangling.html', 'w')
            f.write(output)
            f.close()

            return render_template('resultableImageDangling.html')
        except subprocess.CalledProcessError as e:
            return render_template("500.html", error = str(e))
    else:
        return render_template('login.html')

@app.route('/dockerImageAllDelete', methods=['POST'])
def dkimagealldelete():
    if session.get('logged_in'):
        try:
            outputScript = "docker rmi $(docker images -q) | tee templates/resultableAllImageDelete.txt"
            output = subprocess.check_output(outputScript, shell=True,stderr=subprocess.STDOUT,)
            output = "<h3>cmd = <b>docker rmi $(docker images -q)</b></h3>" + output
            output = "<h2>Docker ALL Image Deletion</h2>" + output
            output = "{% extends \"results.html\" %}{% block body %}<pre>" + output
            output = output + "</pre> {% endblock %}}"
            f = open('templates/resultableAllImageDelete.html', 'w')
            f.write(output)
            f.close()

            return render_template('resultableAllImageDelete.html')
        except subprocess.CalledProcessError as e:
            return render_template("500.html", error = str(e))
    else:
        return render_template('login.html')

@app.route('/dockerContainerKillAll', methods=['POST'])
def dkcontainerkillall():
    if session.get('logged_in'):
        try:
            outputScript = "docker kill $(docker ps -q)" + " | tee templates/resultableTainerKillAll.txt"
            output = subprocess.check_output(outputScript, shell=True,stderr=subprocess.STDOUT,)
            output = "<h3>cmd = <b>docker kill $(docker ps -q)</b></h3>" + output
            output = "<h2>Docker Kill ALL Containers</h2>" + output
            output = "{% extends \"results.html\" %}{% block body %}<pre>" + output
            output = output + "</pre> {% endblock %}}"
            f = open('templates/resultableTainerKillAll.html', 'w')
            f.write(output)
            f.close()

            return render_template('resultableTainerKillAll.html')
        except subprocess.CalledProcessError as e:
            return render_template("500.html", error = str(e))
    else:
        return render_template('login.html')

@app.route('/dockerContainerDeleteAll', methods=['POST'])
def dkcontainerdeleteall():
    if session.get('logged_in'):
        try:
            outputScript = "docker rm $(docker ps -a -q)" + " | tee templates/resultableTainerDeleteAll.txt"
            output = subprocess.check_output(outputScript, shell=True,stderr=subprocess.STDOUT,)
            output = "<h3>cmd = <b>docker rm $(docker ps -a -q)</b></h3>" + output
            output = "<h2>Docker ALL Container Deletion</h2>" + output
            output = "{% extends \"results.html\" %}{% block body %}<pre>" + output
            output = output + "</pre> {% endblock %}}"
            f = open('templates/resultableTainerDeleteAll.html', 'w')
            f.write(output)
            f.close()

            return render_template('resultableTainerDeleteAll.html')
        except subprocess.CalledProcessError as e:
            return render_template("500.html", error = str(e))
    else:
        return render_template('login.html')

@app.route('/dockerContainerStart', methods=['POST'])
def dkcontainerstart():
    if session.get('logged_in'):
        try:
            POST_CONTAINERNAME = str(request.form['containerNameStart'])
            outputScript = "docker start " + POST_CONTAINERNAME + " | tee templates/resultableTainerStart.txt"
            output = subprocess.check_output(outputScript, shell=True,stderr=subprocess.STDOUT,)
            output = "<h3>cmd = <b>docker start "+ POST_CONTAINERNAME +"</b></h3>" + output
            output = "<h2>Docker Container" + POST_CONTAINERNAME + " Start</h2>" + output
            output = "{% extends \"results.html\" %}{% block body %}<pre>" + output
            output = output + "</pre> {% endblock %}}"
            f = open('templates/resultableTainerStart.html', 'w')
            f.write(output)
            f.close()

            return render_template('resultableTainerStart.html')
            #return outputScript
        except subprocess.CalledProcessError as e:
            return render_template("500.html", error = str(e))
    else:
        return render_template('login.html')

@app.route('/dockerContainerStop', methods=['POST'])
def dkcontainerstop():
    if session.get('logged_in'):
        try:
            POST_CONTAINERNAME = str(request.form['containerNameStop'])
            outputScript = "docker stop " + POST_CONTAINERNAME + " | tee templates/resultableTainerStop.txt"
            output = subprocess.check_output(outputScript, shell=True,stderr=subprocess.STDOUT,)
            output = "<h3>cmd = <b>docker stop "+ POST_CONTAINERNAME +"</b></h3>" + output
            output = "<h2>Docker Container" + POST_CONTAINERNAME + " Stop</h2>" + output
            output = "{% extends \"results.html\" %}{% block body %}<pre>" + output
            output = output + "</pre> {% endblock %}}"
            f = open('templates/resultableTainerStop.html', 'w')
            f.write(output)
            f.close()

            return render_template('resultableTainerStop.html')
        except subprocess.CalledProcessError as e:
            return render_template("500.html", error = str(e))
    else:
        return render_template('login.html')

@app.route('/dockerContainerRestart', methods=['POST'])
def dkcontainerrestart():
    if session.get('logged_in'):
        try:
            POST_CONTAINERNAME = str(request.form['containerNameRestart'])
            outputScript = "docker restart " + POST_CONTAINERNAME + " | tee templates/resultableTainerRestart.txt"
            output = subprocess.check_output(outputScript, shell=True,stderr=subprocess.STDOUT,)
            output = "<h3>cmd = <b>docker restart "+ POST_CONTAINERNAME +"</b></h3>" + output
            output = "<h2>Docker Container" + POST_CONTAINERNAME + "restart</h2>" + output
            output = "{% extends \"results.html\" %}{% block body %}<pre>" + output
            output = output + "</pre> {% endblock %}}"
            f = open('templates/resultableTainerRestart.html', 'w')
            f.write(output)
            f.close()

            return render_template('resultableTainerRestart.html')
        except subprocess.CalledProcessError as e:
            return render_template("500.html", error = str(e))
    else:
        return render_template('login.html')

@app.route('/dockerContainerLogs', methods=['POST'])
def dkcontainerlogs():
    if session.get('logged_in'):
        try:
            POST_CONTAINERNAME = str(request.form['containerNameLogs'])
            outputScript = "docker logs --details " + POST_CONTAINERNAME + " | tee templates/resultableTainerLogs.txt"
            output = subprocess.check_output(outputScript, shell=True,stderr=subprocess.STDOUT,)
            output = "<h3>cmd = <b>docker logs --details "+ POST_CONTAINERNAME +"</b></h3>" + output
            output = "<h2>Docker Container Logs " + POST_CONTAINERNAME + " </h2> " + output
            output = "{% extends \"results.html\" %}{% block body %}<pre>" + output
            output = output + "</pre> {% endblock %}}"
            f = open('templates/resultableTainerLogs.html', 'w')
            f.write(output)
            f.close()

            return render_template('resultableTainerLogs.html')
        except subprocess.CalledProcessError as e:
            return render_template("500.html", error = str(e))
    else:
        return render_template('login.html')

@app.route('/dockerContainerStats', methods=['POST'])
def dkcontainerstats():
    if session.get('logged_in'):
        try:
            POST_CONTAINERNAME = str(request.form['containerStats'])
            outputScript = "docker stats --no-stream " + POST_CONTAINERNAME + " | tee templates/resultableStats.txt"
            output = subprocess.check_output(outputScript, shell=True,stderr=subprocess.STDOUT,)
            for i in range(1,3):
                output1 = subprocess.check_output(outputScript, shell=True,stderr=subprocess.STDOUT,)
                output  = output + output1
            output = "<h3>cmd = <b>docker stats --no-stream "+ POST_CONTAINERNAME +"</b></h3>" + output
            output = "<h2>Docker Container Statistics " + POST_CONTAINERNAME + " </h2> " + output
            output = "{% extends \"results.html\" %}{% block body %}<pre>" + output
            output = output + "</pre> {% endblock %}}"
            f = open('templates/resultableStats.html', 'w')
            f.write(output)
            f.close()

            return render_template('resultableStats.html')
        except subprocess.CalledProcessError as e:
            return render_template("500.html", error = str(e))
    else:
        return render_template('login.html')

@app.route('/dockerContainerConfig', methods=['POST'])
def dkcontainerconfig():
    if session.get('logged_in'):
        try:
            POST_CONTAINERNAME = str(request.form['containerConfig'])
            outputScript = "docker inspect --format='{{json .Config}}' " + POST_CONTAINERNAME + "| jq '.' | tee templates/resultableConfig.txt"
            output = subprocess.check_output(outputScript, shell=True,stderr=subprocess.STDOUT,)
            output = "<h2>Docker Container Config " + POST_CONTAINERNAME + " </h2>" + output
            output = "{% extends \"results.html\" %}{% block body %}<pre>" + output
            output = output + "</pre> {% endblock %}}"
            f = open('templates/resultableConfig.html', 'w')
            f.write(output)
            f.close()

            return render_template('resultableConfig.html')
        except subprocess.CalledProcessError as e:
            return render_template("500.html", error = str(e))
    else:
        return render_template('login.html')

@app.route('/dockerContainerHostConfig', methods=['POST'])
def dkcontainerhostconfig():
    if session.get('logged_in'):
        try:
            POST_CONTAINERNAME = str(request.form['containerHostConfig'])
            outputScript = "docker inspect --format='{{json .HostConfig}}' " + POST_CONTAINERNAME + " | jq '.' |tee templates/resultableHostConfig.txt"
            output = subprocess.check_output(outputScript, shell=True,stderr=subprocess.STDOUT,)
            #output = "<h3>cmd = <b>docker inspect --format='{{json .HostConfig}}' "+ POST_CONTAINERNAME +" | jq </b></h3>" + output
            output = "<h2>Docker Container Host Config " + POST_CONTAINERNAME + " </h2> " + output
            output = "{% extends \"results.html\" %}{% block body %}<pre>" + output
            output = output + "</pre> {% endblock %}}"
            f = open('templates/resultableHostConfig.html', 'w')
            f.write(output)
            f.close()

            return render_template('resultableHostConfig.html')
        except subprocess.CalledProcessError as e:
            return render_template("500.html", error = str(e))
    else:
        return render_template('login.html')

@app.route('/dockerContainerNetworkSettings', methods=['POST'])
def dkcontainernetworksettings():
    if session.get('logged_in'):
        try:
            POST_CONTAINERNAME = str(request.form['containerNetworkSettings'])
            outputScript = "docker inspect --format='{{json .NetworkSettings}}' " + POST_CONTAINERNAME + " | jq '.' | tee templates/resultableNetworkSettings.txt"
            output = subprocess.check_output(outputScript, shell=True,stderr=subprocess.STDOUT,)
            #output = "<h3>cmd = <b>docker inspect --format='{{json .HostConfig}}' "+ POST_CONTAINERNAME +" | jq </b></h3>" + output
            output = "<h2>Docker Container Network Settings " + POST_CONTAINERNAME + " </h2> " + output
            output = "{% extends \"results.html\" %}{% block body %}<pre>" + output
            output = output + "</pre> {% endblock %}}"
            f = open('templates/resultableNetworkSettings.html', 'w')
            f.write(output)
            f.close()

            return render_template('resultableNetworkSettings.html')
        except subprocess.CalledProcessError as e:
            return render_template("500.html", error = str(e))
    else:
        return render_template('login.html')

@app.route('/dockerContainerIPaddress', methods=['POST'])
def dkcontaineripaddress():
    if session.get('logged_in'):
        try:
            POST_CONTAINERNAME = str(request.form['containerIPaddress'])
            outputScript = "docker inspect " + POST_CONTAINERNAME + " --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' | tee templates/resultableIPAddress.txt"
            output = subprocess.check_output(outputScript, shell=True,stderr=subprocess.STDOUT,)
            #output = "<h3>cmd = <b>docker inspect --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' " + POST_CONTAINERNAME + " </b></h3>" + output
            output = "<h2>Docker Container " + POST_CONTAINERNAME + " IP Address </h2>" + output
            output = "{% extends \"results.html\" %}{% block body %}<pre>" + output
            output = output + "</pre> {% endblock %}}"
            f = open('templates/resultableIPAddress.html', 'w')
            f.write(output)
            f.close()

            return render_template('resultableIPAddress.html')
        except subprocess.CalledProcessError as e:
            return render_template("500.html", error = str(e))
    else:
        return render_template('login.html')

@app.route('/dockerContainerMounts', methods=['POST'])
def dkcontainermounts():
    if session.get('logged_in'):
        try:
            POST_CONTAINERNAME = str(request.form['containerMounts'])
            outputScript = "docker inspect --format='{{json .Mounts}}' " + POST_CONTAINERNAME + " | jq '.' |tee templates/resultableMounts.txt"
            output = subprocess.check_output(outputScript, shell=True,stderr=subprocess.STDOUT,)
            #output = "<h3>cmd = <b>docker inspect --format='{{.Mounts}}'"+ POST_CONTAINERNAME +"</b></h3>" + output
            output = "<h2>Docker Container " + POST_CONTAINERNAME + " Mounts </h2>" + output
            output = "{% extends \"results.html\" %}{% block body %}<pre>" + output
            output = output + "</pre> {% endblock %}}"
            f = open('templates/resultableMounts.html', 'w')
            f.write(output)
            f.close()

            return render_template('resultableMounts.html')
        except subprocess.CalledProcessError as e:
            return render_template("500.html", error = str(e))
    else:
        return render_template('login.html')

@app.route('/dockerComposeBuild', methods=['POST'])
def dkcomposebuild():
    if session.get('logged_in'):
        try:
            POST_COMPOSEDIR = str(request.form['composePath'])
            outputScript = "docker-compose -f " + POST_COMPOSEDIR + "/docker-compose.yml build --no-cache | tee templates/resultableComposeBuild.txt"
            output = subprocess.check_output(outputScript, shell=True,stderr=subprocess.STDOUT,)
            output = "<h3>cmd = <b>docker-compose -f " + POST_COMPOSEDIR + "/docker-compose.yml build --no-cache</b></h3>" + output
            output = "<h2>Docker Compose Build </h2>" + output
            output = "{% extends \"results.html\" %}{% block body %}<pre>" + output
            output = output + "</pre> {% endblock %}}"
            f = open('templates/resultableComposeBuild.html', 'w')
            f.write(output)
            f.close()

            return render_template('resultableComposeBuild.html')
            return outputScript
        except subprocess.CalledProcessError as e:
            return render_template("500.html", error = str(e))
    else:
        return render_template('login.html')

@app.route('/dockerComposeRun', methods=['POST'])
def dkcomposerun():
    if session.get('logged_in'):
        try:
            POST_COMPOSEDIR = str(request.form['composePath'])
            outputScript = "docker-compose -f " + POST_COMPOSEDIR + "/docker-compose.yml up -d | tee templates/resultableComposeRun.txt"
            output = subprocess.check_output(outputScript, shell=True,stderr=subprocess.STDOUT,)
            output = "<h3>cmd = <b>docker-compose -f " + POST_COMPOSEDIR + "/docker-compose.yml up -d</b></h3>" + output
            output = "<h2>Docker Compose Run </h2>" + output
            output = "{% extends \"results.html\" %}{% block body %}<pre>" + output
            output = output + "</pre> {% endblock %}}"
            f = open('templates/resultableComposeRun.html', 'w')
            f.write(output)
            f.close()

            return render_template('resultableComposeRun.html')
            #return outputScript
        except subprocess.CalledProcessError as e:
            return render_template("500.html", error = str(e))
    else:
        return render_template('login.html')

@app.route('/dockerComposeStop', methods=['POST'])
def dkcomposestop():
    if session.get('logged_in'):
        try:
            POST_COMPOSEDIR = str(request.form['composePath'])
            outputScript = "docker-compose -f " + POST_COMPOSEDIR + "/docker-compose.yml stop | tee templates/resultableComposeStop.txt"
            output = subprocess.check_output(outputScript, shell=True,stderr=subprocess.STDOUT,)
            output = "<h3>cmd = <b>docker-compose -f " + POST_COMPOSEDIR + "/docker-compose.yml stop</b></h3>" + output
            output = "<h2>Docker Compose Stop </h2>" + output
            output = "{% extends \"results.html\" %}{% block body %}<pre>" + output
            output = output + "</pre> {% endblock %}}"
            f = open('templates/resultableComposeStop.html', 'w')
            f.write(output)
            f.close()

            return render_template('resultableComposeStop.html')
            #return outputScript
        except subprocess.CalledProcessError as e:
            return render_template("500.html", error = str(e))
    else:
        return render_template('login.html')

@app.route('/dockerComposeStart', methods=['POST'])
def dkcomposestart():
    if session.get('logged_in'):
        try:
            POST_COMPOSEDIR = str(request.form['composePath'])
            outputScript = "docker-compose -f " + POST_COMPOSEDIR + "/docker-compose.yml start | tee templates/resultableComposeStart.txt"
            output = subprocess.check_output(outputScript, shell=True,stderr=subprocess.STDOUT,)
            output = "<h3>cmd = <b>docker-compose -f " + POST_COMPOSEDIR + "/docker-compose.yml start</b></h3>" + output
            output = "<h2>Docker Compose Run </h2>" + output
            output = "{% extends \"results.html\" %}{% block body %}<pre>" + output
            output = output + "</pre> {% endblock %}}"
            f = open('templates/resultableComposeStart.html', 'w')
            f.write(output)
            f.close()

            return render_template('resultableComposeStart.html')
            #return outputScript
        except subprocess.CalledProcessError as e:
            return render_template("500.html", error = str(e))
    else:
        return render_template('login.html')

#######################
### End mgmt routes ###
#######################

if __name__ == "__main__":

    app.run(debug=True,host='0.0.0.0', port=4096)
