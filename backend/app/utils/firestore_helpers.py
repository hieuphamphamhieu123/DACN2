"""
Helper functions for Firestore operations
"""
from typing import Dict, List, Any, Optional
from datetime import datetime

def doc_to_dict(doc) -> Optional[Dict[str, Any]]:
    """Convert Firestore document to dictionary with id"""
    if not doc or not doc.exists:
        return None
    data = doc.to_dict()
    data['id'] = doc.id
    data['_id'] = doc.id  # For backward compatibility
    return data

def docs_to_list(docs) -> List[Dict[str, Any]]:
    """Convert list of Firestore documents to list of dictionaries"""
    return [doc_to_dict(doc) for doc in docs if doc.exists]

def prepare_doc_for_firestore(doc_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepare document for Firestore by removing None values and converting dates
    """
    cleaned = {}
    for key, value in doc_dict.items():
        if value is not None:
            # Firestore handles datetime objects natively
            cleaned[key] = value
    return cleaned
