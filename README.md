<html><p><span style="font-size: 18px; background:black; color:white"><b><i>&nbsp;tainers</i></b></span><span style="font-size: 18px; background:black; color:#EE82EE"><b><i>Up&nbsp;&#9658;</i></b></span>&nbsp;
</p></html>

## An admin console and learning tool for Docker container technology.

Features:
* Web console display and control of common docker commands.
* Reference diagrams and description for docker concepts.
* Admin and user authorization profiles.
* User credential and profile control from admin_role.
* Issue tracking for clients by company, department, etc.
* Easy to extend capabilities of tainersUp.
* Great for container development.
* Updates for Kubernetes.  

Dependencies:
* Due to path issues this code will only perform on Linux/OS X installations.
* Tested on Python 2.7 but may run on Python 3.X
* Tested on OS X EL Capitan - 10.11.4
* Flask framework for web presentation.
* Tested against Docker Version: 18.05.0-ce
* jq utility for certain docker inspection functions
* chrome or firefox browser due to html 5 constraints.

Installation:

1. mkdir tainersUp
1. cd to tainersUp directory.
1. git clone or download the repository for tainersUp.

Developers Note:
My style is to create the virtualenv inside the root directory of the application.
It's named "flask" to tell the admin / developer clearly what tech is delivering the website.
app.py is configured to start against the path, "#! flask/bin/python"
pip and virtualenv will need to be installed.

OS X
* easy_install virtualenv
* easy_install pip

Linux
1. Debian: apt-get python-virtualenv
1. Fedora: sudo yum install python-setuptools; sudo easy_install virtualenv
1. pip https://packaging.python.org/guides/installing-using-linux-tools/
1. virtualenv flask
1. source flask/bin/activate
1. pip install -r requirements.txt
1. chmod 744 app.py

Starting tainersUp:
1. ./app.py to start application.
1. http://localhost:4096
1. default credentials are tuadmin / !qaz

Stopping tainersUp:
1. cntrl-c to kill server process
1. deactivate <== to turn off virtual environment
