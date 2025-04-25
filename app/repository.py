from typing import List, Optional, Dict
from datetime import datetime
from app import db
from app.models import Contact

class ContactRepository:
    """Repository pattern implementation for Contact model"""
    
    @staticmethod
    def get_all() -> List[Dict]:
        """Get all contacts as serialized dictionaries"""
        contacts = Contact.query.all()
        return [contact.to_dict() for contact in contacts]
    
    @staticmethod
    def get_by_id(contact_id: int) -> Optional[Dict]:
        """Get single contact by ID as serialized dictionary"""
        contact = Contact.query.get(contact_id)
        return contact.to_dict() if contact else None
    
    @staticmethod
    def create(contact_data: Dict) -> Dict:
        """Create new contact and return serialized dictionary"""
        contact = Contact(
            name=contact_data['name'].strip(),
            email=contact_data['email'].strip(),
            message=contact_data['message'].strip()
        )
        db.session.add(contact)
        db.session.commit()
        return contact.to_dict()
    
    @staticmethod
    def update(contact_id: int, contact_data: Dict) -> Optional[Dict]:
        """Update existing contact and return serialized dictionary"""
        contact = Contact.query.get(contact_id)
        if not contact:
            return None
            
        contact.name = contact_data['name'].strip()
        contact.email = contact_data['email'].strip()
        contact.message = contact_data['message'].strip()
        db.session.commit()
        return contact.to_dict()
    
    @staticmethod
    def delete(contact_id: int) -> Dict:
        """Delete contact by ID and return status dictionary"""
        contact = Contact.query.get(contact_id)
        if not contact:
            return {'success': False, 'message': 'Contact not found'}
            
        db.session.delete(contact)
        db.session.commit()
        return {'success': True, 'message': 'Contact deleted'}