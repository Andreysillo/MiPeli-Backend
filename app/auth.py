from collections.abc import Callable

import firebase_admin
from firebase_admin import auth, credentials
from google.auth.credentials import AnonymousCredentials

# Adapter: el resto de la app solo conoce "verify(token) -> uid"; Firebase queda aquí.
# Verificar tokens no necesita cuenta de servicio: basta el projectId (las claves públicas las baja la librería).
# Pero firebase-admin 7 exige un objeto de credenciales al abrir el cliente: se le da uno vacío (no firma nada).
Verifier = Callable[[str], str]


class _NoCredential(credentials.Base):
    def get_credential(self):
        return AnonymousCredentials()


def firebase_verifier(project_id: str) -> Verifier:
    app = firebase_admin.initialize_app(_NoCredential(), {"projectId": project_id}, name=f"verify-{project_id}")

    def verify(token: str) -> str:
        return auth.verify_id_token(token, app=app)["uid"]

    return verify
