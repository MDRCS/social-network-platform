from dotenv import load_dotenv
import os

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SSL_REDIRECT = False
    UPLOAD_FOLDER = "/Users/MDRAHALI/Desktop/Learning_Roadmap/social-network-platform/static/images"
    STATIC_IMAGE_URL = "images"
    HOSTNAME = "0.0.0.0:5000"
    AWS_BUCKET = "social-network-img-upload-aws-s3"
    AWS_CONTENT_URL = "https://s3-us-west-2.amazonaws.com"


class DevelopmentConfig(Config):
    DEBUG = True
    MONGODB_NAME = os.environ.get('MONGODB_DEV_NAME')
    AWS_SEND_MAIL= False

class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    MONGODB_NAME = os.environ.get('MONGODB_TEST_NAME')
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    MONGODB_NAME = os.environ.get('MONGODB_PROD_NAME')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
