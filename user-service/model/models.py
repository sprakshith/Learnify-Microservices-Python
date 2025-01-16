import os
import pymysql
from dotenv import load_dotenv
from enum import Enum as PyEnum
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Enum as SQLEnum, UniqueConstraint

load_dotenv()

USER = os.getenv('MYSQL_USER')
PASSWORD = os.getenv('MYSQL_PASSWORD')
HOST = os.getenv('MYSQL_HOST')
PORT = os.getenv('MYSQL_PORT')
DATABASE = os.getenv('MYSQL_DB')

Base = declarative_base()


class UserRoleEnum(PyEnum):
    STUDENT = "STUDENT"
    TEACHER = "TEACHER"
    ADMIN = "ADMIN"


class User(Base):
    __tablename__ = 'learnify-p-user'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False)
    password = Column(String(100), nullable=False)
    role = Column(SQLEnum(UserRoleEnum), nullable=False)


class Enrollment(Base):
    __tablename__ = 'learnify-p-enrolment'

    id = Column(Integer, primary_key=True)
    course_id = Column(String(50), nullable=False)
    student_id = Column(Integer, nullable=False)

    __table_args__ = (UniqueConstraint('course_id', 'student_id', name='_course_student_uc'),)


def initiate_database():
    conn = pymysql.connect(host=HOST, user=USER, password=PASSWORD, port=int(PORT))
    cursor = conn.cursor()
    create_database_sql = f"CREATE DATABASE IF NOT EXISTS `{DATABASE}`"
    cursor.execute(create_database_sql)
    cursor.close()
    conn.close()

    engine = create_engine(f'mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}')

    Base.metadata.create_all(engine)


def get_session():
    initiate_database()

    engine = create_engine(f'mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}')
    Session = sessionmaker(bind=engine)

    return Session()
