from google.cloud.sql.connector import Connector
import pymysql
from dotenv import load_dotenv
import os

load_dotenv()

connector = Connector()

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")
PROJECT_ID = os.getenv("PROJECT_ID")

def getconn():
    conn = connector.connect(
        PROJECT_ID,
        "pymysql",
        user=DB_USER,
        password=DB_PASS,
        db=DB_NAME
    )
    
    return conn