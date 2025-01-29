import firebase_admin
from firebase_admin import credentials, firestore
from typing import Optional
from . import WorkflowContext

class FirebaseWrapper:
    _initialized = False

    @classmethod
    def initialize(cls, config_path: Optional[str] = None):
        if not cls._initialized:
            if config_path:
                cred = credentials.Certificate(config_path)
            else:
                cred = credentials.ApplicationDefault()

            firebase_admin.initialize_app(cred)
            cls._initialized = True

    @classmethod
    def get_context(cls, doc_id: str) -> WorkflowContext:
        db = firestore.client()
        doc_ref = db.collection('workflows').document(doc_id)
        doc = doc_ref.get()

        if doc.exists:
            data = doc.to_dict()
            context = WorkflowContext(firebase_config=True)
            context.data = data.get('data', {})
            context.execution_log = data.get('execution_log', [])
            return context
        return WorkflowContext(firebase_config=True)

    @classmethod
    def save_context(cls, doc_id: str, context: WorkflowContext):
        db = firestore.client()
        doc_ref = db.collection('workflows').document(doc_id)
        doc_ref.set({
            'data': context.data,
            'execution_log': context.execution_log,
            'timestamp': firestore.SERVER_TIMESTAMP
        })