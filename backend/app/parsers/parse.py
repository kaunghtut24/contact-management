"""
Simplified parser focused on text extraction for Content Intelligence Service
Removes heavy OCR dependencies and focuses on LLM-based processing
"""
import fitz  # PyMuPDF
from docx import Document
import io
import re
import logging
from typing import List, Dict, Any
import vobject

logger = logging.getLogger(__name__)

def extract_text_from_pdf(content: bytes) -> str:
    """Extract text from PDF content"""
    try:
        doc = fitz.open(stream=content, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        logger.error(f"PDF text extraction failed: {e}")
        return ""

def extract_text_from_docx(content: bytes) -> str:
    """Extract text from DOCX content"""
    try:
        doc = Document(io.BytesIO(content))
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        logger.error(f"DOCX text extraction failed: {e}")
        return ""

def parse_csv_content(content: bytes) -> List[Dict[str, str]]:
    """Parse CSV content and return list of contacts"""
    try:
        import csv
        
        content_str = content.decode('utf-8', errors='ignore')
        csv_reader = csv.DictReader(io.StringIO(content_str))
        
        contacts = []
        for row in csv_reader:
            # Map common CSV column names to our schema
            contact = {
                "name": row.get("name", row.get("Name", row.get("NAME", ""))),
                "designation": row.get("designation", row.get("Designation", row.get("title", row.get("Title", "")))),
                "company": row.get("company", row.get("Company", row.get("organization", row.get("Organization", "")))),
                "email": row.get("email", row.get("Email", row.get("EMAIL", ""))),
                "phone": row.get("phone", row.get("Phone", row.get("telephone", row.get("Telephone", "")))),
                "website": row.get("website", row.get("Website", row.get("url", row.get("URL", "")))),
                "address": row.get("address", row.get("Address", row.get("location", row.get("Location", "")))),
                "categories": "Others"
            }
            contacts.append(contact)
        
        return contacts
    except Exception as e:
        logger.error(f"CSV parsing failed: {e}")
        return []

def parse_vcard_content(content: bytes) -> List[Dict[str, str]]:
    """Parse VCF/vCard content"""
    try:
        content_str = content.decode('utf-8', errors='ignore')
        contacts = []
        
        # Parse vCard objects
        for vcard in vobject.readComponents(content_str):
            if vcard.name == 'VCARD':
                contact = {
                    "name": "",
                    "designation": "",
                    "company": "",
                    "email": "",
                    "phone": "",
                    "website": "",
                    "address": "",
                    "categories": "Others"
                }
                
                # Extract name
                if hasattr(vcard, 'fn'):
                    contact["name"] = str(vcard.fn.value)
                elif hasattr(vcard, 'n'):
                    n = vcard.n.value
                    contact["name"] = f"{n.given} {n.family}".strip()
                
                # Extract organization
                if hasattr(vcard, 'org'):
                    contact["company"] = str(vcard.org.value[0]) if vcard.org.value else ""
                
                # Extract title/designation
                if hasattr(vcard, 'title'):
                    contact["designation"] = str(vcard.title.value)
                
                # Extract email
                if hasattr(vcard, 'email'):
                    contact["email"] = str(vcard.email.value)
                
                # Extract phone
                if hasattr(vcard, 'tel'):
                    contact["phone"] = str(vcard.tel.value)
                
                # Extract URL
                if hasattr(vcard, 'url'):
                    contact["website"] = str(vcard.url.value)
                
                # Extract address
                if hasattr(vcard, 'adr'):
                    adr = vcard.adr.value
                    address_parts = [adr.street, adr.city, adr.region, adr.code, adr.country]
                    contact["address"] = ", ".join([part for part in address_parts if part])
                
                contacts.append(contact)
        
        return contacts
    except Exception as e:
        logger.error(f"VCard parsing failed: {e}")
        return []

def extract_contacts_basic_rules(text: str) -> List[Dict[str, str]]:
    """Basic rule-based contact extraction as fallback"""
    try:
        # Basic patterns
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_pattern = r'[\+]?[1-9]?[\d\s\-\(\)]{8,15}'
        
        emails = re.findall(email_pattern, text, re.IGNORECASE)
        phones = re.findall(phone_pattern, text)
        
        # Simple extraction - one contact per email found
        contacts = []
        lines = text.split('\n')
        
        for email in emails:
            contact = {
                "name": "",
                "designation": "",
                "company": "",
                "email": email,
                "phone": phones[0] if phones else "",
                "website": "",
                "address": "",
                "categories": "Others"
            }
            
            # Try to find name and company near email
            for i, line in enumerate(lines):
                if email in line:
                    # Look for name in previous lines
                    for j in range(max(0, i-3), i):
                        if lines[j].strip() and not any(char in lines[j] for char in '@.com'):
                            contact["name"] = lines[j].strip()
                            break
                    break
            
            contacts.append(contact)
        
        return contacts if contacts else [{
            "name": "",
            "designation": "",
            "company": "",
            "email": "",
            "phone": phones[0] if phones else "",
            "website": "",
            "address": "",
            "categories": "Others"
        }]
    except Exception as e:
        logger.error(f"Basic rule extraction failed: {e}")
        return []

# Legacy function names for compatibility (these now just do text extraction)
def parse_pdf(content: bytes) -> List[Dict[str, str]]:
    """Legacy PDF parsing - now just extracts text for Content Intelligence"""
    text = extract_text_from_pdf(content)
    return extract_contacts_basic_rules(text)

def parse_docx(content: bytes) -> List[Dict[str, str]]:
    """Legacy DOCX parsing - now just extracts text for Content Intelligence"""
    text = extract_text_from_docx(content)
    return extract_contacts_basic_rules(text)

def parse_image_fast(content: bytes) -> List[Dict[str, str]]:
    """Legacy image parsing - now returns empty (use OCR microservice instead)"""
    logger.warning("⚠️ Local OCR disabled - use OCR microservice for image processing")
    return []

def parse_image(content: bytes) -> List[Dict[str, str]]:
    """Legacy image parsing - now returns empty (use OCR microservice instead)"""
    logger.warning("⚠️ Local OCR disabled - use OCR microservice for image processing")
    return []

# Remove all OCR-related functions to reduce dependencies
# Images should be processed via the OCR microservice or Content Intelligence Service
