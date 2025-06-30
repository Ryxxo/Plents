import firebase_admin
from firebase_admin import credentials, auth, firestore

# Inicializa Firebase con la clave de servicio
cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred)

# Firestore y Auth quedan disponibles así:
db = firestore.client()
