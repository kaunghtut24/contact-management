"""
vCard (.vcf) file parser for contact extraction
"""
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def parse_vcard_fallback(content: str) -> List[Dict[str, Any]]:
    """Fallback vCard parser using basic text processing"""
    contacts = []
    current_contact = None
    
    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Start of new vCard
        if line.upper().startswith('BEGIN:VCARD'):
            current_contact = {
                'name': '',
                'email': '',
                'phone': '',
                'address': '',
                'category': 'Uncategorized',
                'notes': ''
            }
        
        # End of vCard
        elif line.upper().startswith('END:VCARD'):
            if current_contact and (current_contact['name'] or current_contact['email'] or current_contact['phone']):
                contacts.append(current_contact)
            current_contact = None
        
        # Parse vCard properties
        elif current_contact and ':' in line:
            prop, value = line.split(':', 1)
            prop = prop.upper()
            
            # Full name
            if prop.startswith('FN'):
                current_contact['name'] = value
            
            # Structured name (fallback if FN not present)
            elif prop.startswith('N') and not current_contact['name']:
                # N:Last;First;Middle;Prefix;Suffix
                name_parts = value.split(';')
                if len(name_parts) >= 2:
                    first = name_parts[1] if len(name_parts) > 1 else ''
                    last = name_parts[0] if name_parts[0] else ''
                    current_contact['name'] = f"{first} {last}".strip()
            
            # Email
            elif prop.startswith('EMAIL'):
                if not current_contact['email']:  # Take first email
                    current_contact['email'] = value
                else:
                    # Add additional emails to notes
                    if current_contact['notes']:
                        current_contact['notes'] += f"; Additional email: {value}"
                    else:
                        current_contact['notes'] = f"Additional email: {value}"
            
            # Phone
            elif prop.startswith('TEL'):
                if not current_contact['phone']:  # Take first phone
                    current_contact['phone'] = value
                else:
                    # Add additional phones to notes
                    if current_contact['notes']:
                        current_contact['notes'] += f"; Additional phone: {value}"
                    else:
                        current_contact['notes'] = f"Additional phone: {value}"
            
            # Address
            elif prop.startswith('ADR'):
                # ADR:;;Street;City;State;PostalCode;Country
                addr_parts = value.split(';')
                address_components = []
                
                if len(addr_parts) > 2 and addr_parts[2]:  # Street
                    address_components.append(addr_parts[2])
                if len(addr_parts) > 3 and addr_parts[3]:  # City
                    address_components.append(addr_parts[3])
                if len(addr_parts) > 4 and addr_parts[4]:  # State
                    address_components.append(addr_parts[4])
                if len(addr_parts) > 5 and addr_parts[5]:  # Postal Code
                    address_components.append(addr_parts[5])
                if len(addr_parts) > 6 and addr_parts[6]:  # Country
                    address_components.append(addr_parts[6])
                
                current_contact['address'] = ', '.join(address_components)
            
            # Organization
            elif prop.startswith('ORG'):
                if current_contact['notes']:
                    current_contact['notes'] += f"; Organization: {value}"
                else:
                    current_contact['notes'] = f"Organization: {value}"
                
                # Set category to Work if organization is present
                current_contact['category'] = 'Work'
            
            # Title/Role
            elif prop.startswith('TITLE'):
                if current_contact['notes']:
                    current_contact['notes'] += f"; Title: {value}"
                else:
                    current_contact['notes'] = f"Title: {value}"
            
            # Note
            elif prop.startswith('NOTE'):
                if current_contact['notes']:
                    current_contact['notes'] += f"; {value}"
                else:
                    current_contact['notes'] = value
    
    return contacts

def parse_vcard_with_vobject(content: str) -> List[Dict[str, Any]]:
    """Parse vCard using vobject library"""
    try:
        import vobject
        contacts = []
        
        # Parse multiple vCards in the content
        vcards = []
        current_vcard = []
        
        for line in content.split('\n'):
            line = line.strip()
            if line.upper().startswith('BEGIN:VCARD'):
                current_vcard = [line]
            elif line.upper().startswith('END:VCARD'):
                current_vcard.append(line)
                vcards.append('\n'.join(current_vcard))
                current_vcard = []
            elif current_vcard:
                current_vcard.append(line)
        
        for vcard_text in vcards:
            try:
                vcard = vobject.readOne(vcard_text)
                contact = {
                    'name': '',
                    'email': '',
                    'phone': '',
                    'address': '',
                    'category': 'Uncategorized',
                    'notes': ''
                }
                
                # Extract name
                if hasattr(vcard, 'fn'):
                    contact['name'] = vcard.fn.value
                elif hasattr(vcard, 'n'):
                    n = vcard.n.value
                    contact['name'] = f"{n.given} {n.family}".strip()
                
                # Extract email
                if hasattr(vcard, 'email'):
                    if isinstance(vcard.email, list):
                        contact['email'] = vcard.email[0].value
                        # Add additional emails to notes
                        if len(vcard.email) > 1:
                            additional_emails = [e.value for e in vcard.email[1:]]
                            contact['notes'] = f"Additional emails: {', '.join(additional_emails)}"
                    else:
                        contact['email'] = vcard.email.value
                
                # Extract phone
                if hasattr(vcard, 'tel'):
                    if isinstance(vcard.tel, list):
                        contact['phone'] = vcard.tel[0].value
                        # Add additional phones to notes
                        if len(vcard.tel) > 1:
                            additional_phones = [t.value for t in vcard.tel[1:]]
                            if contact['notes']:
                                contact['notes'] += f"; Additional phones: {', '.join(additional_phones)}"
                            else:
                                contact['notes'] = f"Additional phones: {', '.join(additional_phones)}"
                    else:
                        contact['phone'] = vcard.tel.value
                
                # Extract address
                if hasattr(vcard, 'adr'):
                    adr = vcard.adr.value if not isinstance(vcard.adr, list) else vcard.adr[0].value
                    address_parts = []
                    if adr.street: address_parts.append(adr.street)
                    if adr.city: address_parts.append(adr.city)
                    if adr.region: address_parts.append(adr.region)
                    if adr.code: address_parts.append(adr.code)
                    if adr.country: address_parts.append(adr.country)
                    contact['address'] = ', '.join(address_parts)
                
                # Extract organization
                if hasattr(vcard, 'org'):
                    org = vcard.org.value[0] if isinstance(vcard.org.value, list) else vcard.org.value
                    if contact['notes']:
                        contact['notes'] += f"; Organization: {org}"
                    else:
                        contact['notes'] = f"Organization: {org}"
                    contact['category'] = 'Work'
                
                # Extract title
                if hasattr(vcard, 'title'):
                    title = vcard.title.value
                    if contact['notes']:
                        contact['notes'] += f"; Title: {title}"
                    else:
                        contact['notes'] = f"Title: {title}"
                
                # Extract note
                if hasattr(vcard, 'note'):
                    note = vcard.note.value
                    if contact['notes']:
                        contact['notes'] += f"; {note}"
                    else:
                        contact['notes'] = note
                
                if contact['name'] or contact['email'] or contact['phone']:
                    contacts.append(contact)
                    
            except Exception as e:
                logger.warning(f"Error parsing individual vCard: {e}")
                continue
        
        return contacts
        
    except ImportError:
        logger.warning("vobject library not available, using fallback parser")
        return parse_vcard_fallback(content)

def parse_vcard(content: str) -> List[Dict[str, Any]]:
    """Main function to parse vCard content"""
    try:
        # Try with vobject first
        return parse_vcard_with_vobject(content)
    except Exception as e:
        logger.warning(f"vobject parsing failed: {e}, using fallback")
        return parse_vcard_fallback(content)
