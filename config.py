import json
import os
from google.cloud import secretmanager


def get_secret(project_id, secret_name, secret_ver):
    client = secretmanager.SecretManagerServiceClient()
    name = client.secret_version_path(project_id, secret_name, secret_ver)
    response = client.access_secret_version(request={"name": name})
    return json.loads(response.payload.data.decode('UTF-8'))


project_id = os.environ.get('PROJECT_ID')
secret_name = os.environ.get('SECRET_NAME')
secret_ver = os.environ.get('SECRET_VERSION')
secrets = get_secret(project_id, secret_name, secret_ver)

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

# User Settings
SAVE_PATH = "twitter_json/{yyyy}/{mm}/"
SAVE_NAME = "{yyyy}{mm}{dd}.json"
SAVE_TO_S3 = True
