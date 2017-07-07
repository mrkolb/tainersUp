from flask import Flask
#import datetime
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tu_tabledef import *
from flask_bcrypt import Bcrypt
from getpass import getpass

app=Flask(__name__)
bcrypt = Bcrypt(app)

def main():
    engine = create_engine('sqlite:///tainersUp.db', echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()

    print 'Creating tuadmin: '
    username = 'tuadmin'
    print 'Enter Password: '
    password = getpass()
    assert password == getpass('Password (again):')

    admin = User(username=username, password=bcrypt.generate_password_hash(password))
    session.add(admin)
    session.commit()
    print 'tuadmin created.'

if __name__ == '__main__':
    sys.exit(main())
