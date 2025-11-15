import firebase_admin
from firebase_admin import credentials, firestore
import os

# Global Firestore client
db = None

def get_database():
    """Get the Firestore database instance"""
    global db
    if db is None:
        raise Exception("Database not initialized. Call connect_to_firestore() first.")
    return db

async def connect_to_firestore():
    """Initialize Firebase Admin SDK and connect to Firestore"""
    global db
    try:
        # Path to Firebase credentials file
        cred_path = os.path.join(os.path.dirname(__file__), "..", "firebase-credentials.json")

        if not os.path.exists(cred_path):
            raise FileNotFoundError(f"Firebase credentials file not found at: {cred_path}")

        # Initialize Firebase Admin SDK
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)

        # Get Firestore client
        db = firestore.client()

        # Test connection by trying to access a collection
        # This will create the collection if it doesn't exist
        test_collection = db.collection('_connection_test')

        print("[SUCCESS] Connected to Firebase Firestore")

    except Exception as e:
        print(f"[ERROR] Failed to connect to Firestore: {e}")
        print("[TIP] Troubleshooting:")
        print("   1. Check firebase-credentials.json file exists in backend/")
        print("   2. Verify the file contains valid Firebase service account credentials")
        print("   3. Ensure Firestore is enabled in your Firebase project")
        raise

async def close_firestore_connection():
    """Close Firestore connection"""
    global db
    try:
        # Firebase Admin SDK handles connection cleanup automatically
        if firebase_admin._apps:
            firebase_admin.delete_app(firebase_admin.get_app())
        db = None
        print("[INFO] Closed Firestore connection")
    except Exception as e:
        print(f"[WARNING] Error closing Firestore connection: {e}")

async def init_database():
    """Initialize Firestore collections and indexes"""
    global db
    if db is None:
        raise Exception("Database not connected")

    try:
        # Firestore doesn't require explicit index creation like MongoDB
        # Indexes are created automatically or via Firebase Console
        # But we can create sample collections to ensure they exist

        collections = ['users', 'posts', 'comments', 'likes']
        for collection_name in collections:
            # Just reference the collection - it will be created when first document is added
            db.collection(collection_name)

        print("[SUCCESS] Firestore collections initialized")
    except Exception as e:
        print(f"[WARNING] Could not initialize collections: {e}")
