import os
import json
import firebase_admin
from firebase_admin import credentials
from django.conf import settings

def initialize_firebase():
    """
    Initializes the Firebase Admin SDK.
    Checks if it's already initialized to prevent errors on Django auto-reload.
    """
    if not firebase_admin._apps:
        creds_json = os.environ.get('FIREBASE_CREDENTIALS')
        
        if creds_json:
            try:
                creds_dict = json.loads(creds_json)
                cred = credentials.Certificate(creds_dict)
                firebase_admin.initialize_app(cred)
                print("Firebase Admin SDK initialized successfully.")
            except Exception as e:
                print(f"Failed to initialize Firebase Admin SDK: {e}")
        else:
            print("FIREBASE_CREDENTIALS environment variable not set. Firebase not initialized.")
