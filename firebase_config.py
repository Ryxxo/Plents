# import pyrebase
import firebase_admin
from firebase_admin import credentials, auth

cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred)


firebase_config = {
    "apiKey": "AIzaSyBorRTmuKdUp93J87FeuenqrGgAUNmXYyc",
    "authDomain": "plents-9fcf2.firebaseapp.com",
    "databaseURL": "https://plents-9fcf2-default-rtdb.firebaseio.com",
    "projectId": "plents-9fcf2",
    "storageBucket": "plents-9fcf2.appspot.com",
    "messagingSenderId": "536770589606",
    "appId": "1:536770589606:web:6d7cb555d8047cf3891567",
    "measurementId": "G-0KCGX1QDHW"
}

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
