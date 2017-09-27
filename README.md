# tainersUp
## An admin console and learning tool for Docker container technology from WebLaminar.


Dependencies:
* Due to path issues this code will only perform on Linux/OS X installations.
* Tested on Python 2.7 but may run on Python 3.X
* Tested on OS X EL Capitan - 10.11.4
* Flask framework for web presentation.
* Tested against Docker Version: 17.06.0-ce

Scope:  docker and docker-compose usage


Installation:

1. mkdir tainersUp
1. cd to tainersUp directory.
1. git clone or download the repository for tainersUp.

Developers Note:
My style is to create the virtualenv inside the root directory of the application.
It's named "flask" to tell the admin / developer clearly what tech is delivering the website.
app.py is configured to start against the path, "#! flask/bin/python"
pip and virtualenv may need to be installed.

OS X
* easy_install virtualenv
* easy_install pip

Linux
1. Debian: apt-get python-virtualenv
1. Fedora: sudo yum install python-setuptools; sudo easy_install virtualenv
1. pip https://packaging.python.org/guides/installing-using-linux-tools/
1. virtualenv flask
1. pip install -r requirements.txt
1. chmod 744 app.py
1. ./app.py to start application.
1. http://localhost:4000
1. default credentials are tuadmin / !qaz

Credential changes:
1. Stop application IF RUNNING.
1. cd to tainersUp directory
1. mv tainersUp.db to new name
1. source flask/bin/activate
1. python create_admin.py
1. add new password for tuadmin and script will bcrypt the password.
1. Start application.
