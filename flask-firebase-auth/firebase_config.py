import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("D:/RiverGuard/Backend/Flask-firebase-auth/Firebase_key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
users_ref = db.collection("users")
