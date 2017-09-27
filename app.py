#! flask/bin/python
from flask import Flask, flash, redirect, render_template, request, session, abort
from flask import url_for, send_from_directory
from werkzeug import secure_filename
import os
import subprocess
from sqlalchemy.orm import sessionmaker
from tu_tabledef import *
from flask_bcrypt import Bcrypt

engine = create_engine('sqlite:///tainersUp.db', echo=True)

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = os.urandom(12)
# Path to the upload directory
app.config['UPLOAD_FOLDER'] = 'uploads/'
# Extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set(['yml', 'yaml'])
# Return whether it's an allowed type or not with an exception for "Dockerfile"
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS'] or filename == "Dockerfile"

@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        #return dkinfo()
        return "Please logout  <a href='/logout'>Logout</a>"

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


@app.route("/dockerinfo")
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

@app.route('/login', methods=['POST'])
def do_admin_login():

    POST_USERNAME = str(request.form['username'])
    POST_PASSWORD = str(request.form['password'])

    Session = sessionmaker(bind=engine)
    s = Session()
    query = s.query(User).filter_by(username='tuadmin').first()
    result = bcrypt.check_password_hash(query.password, POST_PASSWORD) # returns True
    if result:
        session['logged_in'] = True
    else:
        flash('wrong password!')
    return dkinfo()

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

@app.route('/dockerContainerIPaddress', methods=['POST'])
def dkcontaineripaddress():
    if session.get('logged_in'):
        try:
            POST_CONTAINERNAME = str(request.form['containerIPaddress'])
            outputScript = "docker inspect --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}'" + POST_CONTAINERNAME + " | tee templates/resultableIPAddress.txt"
            output = subprocess.check_output(outputScript, shell=True,stderr=subprocess.STDOUT,)
            output = "<h3>cmd = <b>docker inspect --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}'"+ POST_CONTAINERNAME +"</b></h3>" + output
            output = "<h2>Docker Container" + POST_CONTAINERNAME + " IP Address </h2>" + output
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
            outputScript = "docker inspect --format='{{.Mounts}}'" + POST_CONTAINERNAME + " | tee templates/resultableIPAddress.txt"
            output = subprocess.check_output(outputScript, shell=True,stderr=subprocess.STDOUT,)
            output = "<h3>cmd = <b>docker inspect --format='{{.Mounts}}'"+ POST_CONTAINERNAME +"</b></h3>" + output
            output = "<h2>Docker Container" + POST_CONTAINERNAME + " IP Address </h2>" + output
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

    app.run(debug=True,host='0.0.0.0', port=4000)
