import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    # SQLALCHEMY_DATABASE_URI = 'mysql://VivekGoswami:123@rhombuz@demomysqlserver.mysql.database.azure.com/m360'

    db_uri = 'mysql+mysqlconnector://VivekGoswami:123%40rhombuz@demomysqlserver.mysql.database.azure.com:3306/m360?ssl_ca=ca-cert-filename.pem'

    SQLALCHEMY_DATABASE_URI = db_uri

    SQLALCHEMY_TRACK_MODIFICATIONS = False