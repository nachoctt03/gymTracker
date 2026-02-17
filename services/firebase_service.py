import firebase_admin
from firebase_admin import credentials, db
from typing import List, Optional
import os


class FirebaseService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.current_user_id: Optional[str] = None
            self.database_ref = None
            self._initialize_firebase()
            self._initialized = True

    def _initialize_firebase(self):
        try:
            credentials_path = self._find_credentials_file()
            if not credentials_path:
                print("ERROR: No se encontró firebase-credentials.json")
                return

            if not firebase_admin._apps:
                cred = credentials.Certificate(credentials_path)
                firebase_admin.initialize_app(cred, {
                    'databaseURL': 'https://gymtrackerctt-default-rtdb.firebaseio.com/'
                })

            self.database_ref = db.reference()

        except Exception as e:
            print(f"Error al inicializar Firebase: {e}")

    def _find_credentials_file(self) -> Optional[str]:
        possible_paths = [
            'firebase-credentials.json',
            'config/firebase-credentials.json',
            '../firebase-credentials.json',
            os.path.join(os.path.dirname(__file__), 'firebase-credentials.json'),
            os.path.join(os.path.dirname(__file__), '..', 'firebase-credentials.json'),
        ]
        return next((p for p in possible_paths if os.path.exists(p)), None)

    def login(self, email: str, password: str) -> bool:
        try:
            users = self.database_ref.child('usuarios').order_by_child('email').equal_to(email).get()
            if users:
                for user_id, user_data in users.items():
                    if user_data.get('password') == password:
                        self.current_user_id = user_id
                        return True
            return False
        except Exception as e:
            print(f"Error en login: {e}")
            return False

    def registro(self, email: str, password: str, nombre: str) -> bool:
        try:
            users_ref = self.database_ref.child('usuarios')
            if users_ref.order_by_child('email').equal_to(email).get():
                return False

            new_user_ref = users_ref.push()
            new_user_ref.set({'email': email, 'password': password, 'nombre': nombre})
            self.current_user_id = new_user_ref.key
            return True
        except Exception as e:
            print(f"Error en registro: {e}")
            return False

    def guardar_ejercicio(self, ejercicio) -> bool:
        try:
            if not self.current_user_id:
                return False
            ejercicios_ref = self.database_ref.child('usuarios').child(self.current_user_id).child('ejercicios')
            new_ref = ejercicios_ref.push()
            ejercicio.id = new_ref.key
            new_ref.set(ejercicio.to_dict())
            return True
        except Exception as e:
            print(f"Error al guardar ejercicio: {e}")
            return False

    def obtener_ejercicios(self) -> List:
        try:
            if not self.current_user_id:
                return []
            from models.ejercicio import Ejercicio
            data = self.database_ref.child('usuarios').child(self.current_user_id).child('ejercicios').get()
            if not data:
                return []
            return [Ejercicio.from_dict(v, k) for k, v in data.items()]
        except Exception as e:
            print(f"Error al obtener ejercicios: {e}")
            return []

    def eliminar_ejercicio(self, ejercicio_id: str) -> bool:
        try:
            if not self.current_user_id:
                return False
            self.database_ref.child('usuarios').child(self.current_user_id).child('ejercicios').child(ejercicio_id).delete()
            return True
        except Exception as e:
            print(f"Error al eliminar ejercicio: {e}")
            return False

    def get_current_user_id(self) -> Optional[str]:
        return self.current_user_id

    def logout(self):
        self.current_user_id = None
