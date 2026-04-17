from google.cloud.sql.connector import Connector
import pymysql

connector = Connector()

def getconn():
    conn = connector.connect(
        "cs4750-data:us-east4:pets-2",
        "pymysql",
        user="root",
        password="PetsAccessDB4750?",
        db="pet-shelter-1"
    )
    return conn