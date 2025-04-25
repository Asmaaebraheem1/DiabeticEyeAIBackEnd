from typing import Dict, Optional, List
from datetime import datetime
import re
from app.repository import ContactRepository
from app.models import Contact

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_contact_data(data: Dict) -> Dict[str, str]:
    """Validate contact form data"""
    errors = {}
    
    # Name validation
    if not data.get('name') or len(data['name'].strip()) < 2:
        errors['name'] = 'Name must be at least 2 characters'
    
    # Email validation
    if not data.get('email'):
        errors['email'] = 'Email is required'
    elif not validate_email(data['email']):
        errors['email'] = 'Invalid email format'
    
    # Message validation
    if not data.get('message') or len(data['message'].strip()) < 10:
        errors['message'] = 'Message must be at least 10 characters'
    
    return errors

class ContactService:
    """Service layer for contact operations"""
    
    @staticmethod
    def get_all_contacts() -> List[Dict]:
        """Get all contacts as serialized dictionaries"""
        return ContactRepository.get_all()
    
    @staticmethod
    def get_contact(contact_id: int) -> Optional[Dict]:
        """Get single contact by ID as serialized dictionary"""
        return ContactRepository.get_by_id(contact_id)
    
    @staticmethod
    def create_contact(contact_data: Dict) -> Dict:
        """Create new contact with validation"""
        errors = validate_contact_data(contact_data)
        if errors:
            return {'error': 'Validation failed', 'details': errors}
        
        try:
            contact = ContactRepository.create(contact_data)
            return {'message': 'Submitted successfully', 'contact': contact}
        except Exception as e:
            return {'error': 'Failed to save contact', 'details': str(e)}
    
    @staticmethod
    def update_contact(contact_id: int, contact_data: Dict) -> Dict:
        """Update existing contact with validation"""
        errors = validate_contact_data(contact_data)
        if errors:
            return {'error': 'Validation failed', 'details': errors}
        
        contact = ContactRepository.update(contact_id, contact_data)
        if not contact:
            return {'error': 'Contact not found'}
        
        return {'message': 'Contact updated successfully', 'contact': contact}
    
    @staticmethod
    def delete_contact(contact_id: int) -> Dict:
        """Delete contact by ID"""
        result = ContactRepository.delete(contact_id)
        if not result.get('success'):
            return {'error': result.get('message', 'Contact not found')}
        return {'message': result.get('message', 'Contact deleted successfully')}

# Use Cases
class CreateContactUseCase:
    """Use case for creating contacts"""
    
    @staticmethod
    def execute(contact_data: Dict) -> Dict:
        return ContactService.create_contact(contact_data)

class GetContactsUseCase:
    """Use case for getting contacts"""
    
    @staticmethod
    def execute() -> List[Dict]:
        return ContactService.get_all_contacts()

class UpdateContactUseCase:
    """Use case for updating contacts"""
    
    @staticmethod
    def execute(contact_id: int, contact_data: Dict) -> Dict:
        return ContactService.update_contact(contact_id, contact_data)

class DeleteContactUseCase:
    """Use case for deleting contacts"""
    
    @staticmethod
    def execute(contact_id: int) -> Dict:
        return ContactService.delete_contact(contact_id)