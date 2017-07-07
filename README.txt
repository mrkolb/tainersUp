### tainersUp beta v 0.1 ####

Purpose: admin console and learning tool for Docker container technology.

Author:  WebLaminar LLC
         mkolb@weblaminar.com

Date: July 7, 2017

Dependencies:
* Due to path issues this code will only perform on Linux/OS X installations.
* Tested on Python 2.7 but may run on Python 3.X
* Tested on OS X EL Capitan - 10.11.4
* Flask framework for web presentation.
* Tested against Docker Server Version: 17.06.0-ce

Scope:  docker and docker-compose usage


Installation:

1) mkdir tainersUp
2) cd to tainersUp directory.
3) git clone or download the repository for tainersUp.

Developers Note:
My style is to create the virtualenv inside the root directory of the application.
It's named "flask" to tell the admin / developer clearly what tech is delivering the website.
app.py is configured to start against the path, "#! flask/bin/python"
pip and virtualenv may need to be installed.

OS X
* easy_install virtualenv
* easy_install pip

Linux
* Debian: apt-get python-virtualenv
* Fedora: sudo yum install python-setuptools; sudo easy_install virtualenv
* pip https://packaging.python.org/guides/installing-using-linux-tools/

4) virtualenv flask
5) pip install -r requirements.txt
6) chmod 744 app.py
7) ./app.py to start application.
8) http://localhost:4000
9) default credentials are tuadmin / !qaz

Credential changes:
1) Stop application IF RUNNING.
2) cd to tainersUp directory
3) mv tainersUp.db to new name
4) source flask/bin/activate
5) python create_admin.py
6) add new password for tuadmin and script will bcrypt the password.
7) Start application.
