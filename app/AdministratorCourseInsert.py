# Source: https://mysql.wisborg.dk/2019/03/03/using-sqlalchemy-with-mysql-8/

import mysql.connector
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base

#Do not forget to install mysql.connector and sqlalchemy

import db 
# pwd.py contains MyPassword = "1234"
# Username and password are stored in the python file for simplicity
# Do not store user credentials in your code, look for best security practices in your OS, database, and development environment

engine = sqlalchemy.create_engine(
    'mysql+mysqlconnector://root:' + db.password + '@localhost:3306/pricelist',
    echo=True)

# Define and create the table
Base = declarative_base()

# Class Store(name, headquarter, storeType)  <--> Pricelist.stores(name, headquarter, storeType)
class Course(Base):
    __tablename__ = 'courses'
 
    name = sqlalchemy.Column(sqlalchemy.String(length=50), primary_key=True)
    semester = sqlalchemy.Column(sqlalchemy.String(length=50))
    year = sqlalchemy.Column(sqlalchemy.String(length=50))
    summary = sqlalchemy.Column(sqlalchemy.String(length=50))
    professor = sqlalchemy.Column(sqlalchemy.String(length=50))
     
    def __repr__(self):
        return "<Course(name='{0}', semester='{1}', year='{2}', summary='{1}, 'professor='{2}')>".format(
                            self.name, self.headquarters, self.storeType)
 
Base.metadata.create_all(engine) # creates the courses table
 
# Create a session
Session = sqlalchemy.orm.sessionmaker()
Session.configure(bind=engine)
session = Session()

newCourse= Course(name='CS348', semester='Fall', year='2021', summary ='blah blah', professor ='blah blah')
session.add(newCourse)

session.commit()


