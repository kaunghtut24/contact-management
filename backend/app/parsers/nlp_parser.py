"""
Enhanced NLP-based contact parser using SpaCy
"""
import re
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Fallback patterns if SpaCy is not available
EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
PHONE_PATTERN = r'(?:\+?1?[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
INDIAN_PHONE_PATTERN = r'(?:\+?91[-.\s]?)?(?:0\d{2,4}[-.\s]?)?(\d{8,12})'

class NLPContactParser:
    def __init__(self):
        self.nlp = None
        self._load_spacy_model()
    
    def _load_spacy_model(self):
        """Load SpaCy model with fallback"""
        try:
            import spacy
            # Try to load English model
            try:
                self.nlp = spacy.load("en_core_web_sm")
                logger.info("SpaCy English model loaded successfully")
            except OSError:
                logger.warning("SpaCy English model not found, using blank model")
                self.nlp = spacy.blank("en")
        except ImportError:
            logger.warning("SpaCy not available, using regex-based parsing")
            self.nlp = None
    
    def extract_entities_with_spacy(self, text: str) -> Dict[str, List[str]]:
        """Extract entities using SpaCy NLP"""
        if not self.nlp:
            return self._extract_entities_regex(text)
        
        doc = self.nlp(text)
        entities = {
            'persons': [],
            'organizations': [],
            'locations': [],
            'emails': [],
            'phones': []
        }
        
        # Extract named entities
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                entities['persons'].append(ent.text.strip())
            elif ent.label_ in ["ORG", "ORGANIZATION"]:
                entities['organizations'].append(ent.text.strip())
            elif ent.label_ in ["GPE", "LOC", "LOCATION"]:
                entities['locations'].append(ent.text.strip())
        
        # Extract emails and phones using regex (more reliable)
        entities['emails'] = re.findall(EMAIL_PATTERN, text)
        entities['phones'] = self._extract_phone_numbers(text)
        
        return entities
    
    def _extract_entities_regex(self, text: str) -> Dict[str, List[str]]:
        """Fallback regex-based entity extraction"""
        entities = {
            'persons': [],
            'organizations': [],
            'locations': [],
            'emails': [],
            'phones': []
        }
        
        # Extract emails and phones
        entities['emails'] = re.findall(EMAIL_PATTERN, text)
        entities['phones'] = self._extract_phone_numbers(text)
        
        # Simple heuristics for names and organizations
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Skip lines that start with common prefixes
            if line.lower().startswith(('tel', 'fax', 'email', 'phone', 'mobile')):
                continue
            
            # If line has 2-3 words and proper case, likely a person name
            words = line.split()
            if 2 <= len(words) <= 3 and all(word[0].isupper() for word in words if word):
                entities['persons'].append(line)
            
            # If line contains business keywords, likely organization
            business_keywords = ['company', 'corp', 'ltd', 'inc', 'llc', 'organization', 'institute']
            if any(keyword in line.lower() for keyword in business_keywords):
                entities['organizations'].append(line)
        
        return entities
    
    def _extract_phone_numbers(self, text: str) -> List[str]:
        """Extract and clean phone numbers"""
        phones = []
        
        # Find all potential phone numbers
        matches = re.findall(INDIAN_PHONE_PATTERN, text)
        for match in matches:
            if isinstance(match, tuple):
                phone = ''.join(match)
            else:
                phone = match
            
            # Clean and validate
            clean_phone = re.sub(r'\D', '', phone)
            if 8 <= len(clean_phone) <= 15:
                phones.append(clean_phone)
        
        # Also try international pattern
        intl_matches = re.findall(PHONE_PATTERN, text)
        for match in intl_matches:
            phone = ''.join(match)
            clean_phone = re.sub(r'\D', '', phone)
            if 10 <= len(clean_phone) <= 15:
                phones.append(clean_phone)
        
        return list(set(phones))  # Remove duplicates
    
    def parse_contact_text(self, text: str) -> List[Dict[str, Any]]:
        """Parse contact information from text using NLP"""
        entities = self.extract_entities_with_spacy(text)
        contacts = []
        
        # Group entities into contacts
        # If we have emails, use them as contact anchors
        if entities['emails']:
            for email in entities['emails']:
                contact = self._create_contact_from_entities(entities, email)
                contacts.append(contact)
        else:
            # Create contacts based on persons or organizations
            names = entities['persons'] + entities['organizations']
            if names:
                for name in names:
                    contact = self._create_contact_from_entities(entities, name=name)
                    contacts.append(contact)
            else:
                # Fallback: create single contact with available info
                contact = self._create_contact_from_entities(entities)
                if contact['email'] or contact['phone']:
                    contacts.append(contact)
        
        return contacts
    
    def _create_contact_from_entities(self, entities: Dict[str, List[str]], 
                                    email: str = None, name: str = None) -> Dict[str, Any]:
        """Create a contact record from extracted entities"""
        contact = {
            'name': '',
            'email': email or '',
            'phone': '',
            'address': '',
            'category': 'Uncategorized',
            'notes': ''
        }
        
        # Set name
        if name:
            contact['name'] = name
        elif entities['persons']:
            contact['name'] = entities['persons'][0]
        elif entities['organizations']:
            contact['name'] = entities['organizations'][0]
        elif email:
            # Extract name from email
            local_part = email.split('@')[0]
            contact['name'] = local_part.replace('.', ' ').replace('_', ' ').title()
        
        # Set phone
        if entities['phones']:
            contact['phone'] = entities['phones'][0]
        
        # Set address from locations
        if entities['locations']:
            contact['address'] = ', '.join(entities['locations'])
        
        # Add additional info to notes
        notes_parts = []
        if len(entities['phones']) > 1:
            notes_parts.append(f"Additional phones: {', '.join(entities['phones'][1:])}")
        if entities['organizations'] and not contact['name'] in entities['organizations']:
            notes_parts.append(f"Organization: {', '.join(entities['organizations'])}")
        
        contact['notes'] = '; '.join(notes_parts)
        
        return contact

# Global parser instance
nlp_parser = NLPContactParser()

def extract_contacts_nlp(text: str) -> List[Dict[str, Any]]:
    """Main function to extract contacts using NLP"""
    return nlp_parser.parse_contact_text(text)
