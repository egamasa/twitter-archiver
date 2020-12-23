import json
import os
from google.cloud import secretmanager


def get_secrets(project_id, secret_name, secret_ver):
    client = secretmanager.SecretManagerServiceClient()
    name = client.secret_version_path(project_id, secret_name, secret_ver)
    response = client.access_secret_version(request={"name": name})
    return json.loads(response.payload.data.decode('UTF-8'))


PROJECT_ID = os.environ.get('PROJECT_ID')
SECRET_NAME = os.environ.get('SECRET_NAME')
SECRET_VERSION = os.environ.get('SECRET_VERSION')
secrets = get_secrets(PROJECT_ID, SECRET_NAME, SECRET_VERSION)

# Twitter API Keys
CONSUMER_KEY = secrets['CONSUMER_KEY']
CONSUMER_SECRET = secrets['CONSUMER_SECRET']
ACCESS_TOKEN = secrets['ACCESS_TOKEN']
ACCESS_TOKEN_SECRET = secrets['ACCESS_TOKEN_SECRET']

# Object Storage Settings (Compatible with Amazon S3)
ACCESS_KEY_ID = secrets['ACCESS_KEY_ID']
SECRET_ACCESS_KEY = secrets['SECRET_ACCESS_KEY']
# REGION_NAME = ""
ENDPOINT_URL = os.environ.get('ENDPOINT_URL')
BUCKET_NAME = os.environ.get('BUCKET_NAME')

# Google Pub/Sub Settings
TOPIC_ID = os.environ.get('TOPIC_ID')

# Output Settings
SAVE_PATH = "twitter-archiver/{yyyy}/{mm}/"
SAVE_NAME = "{yyyy}{mm}{dd}.json"
SAVE_TO_S3 = True
PUB_TO_IMAGER = True
