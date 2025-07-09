import fitz  # PyMuPDF
from docx import Document
import io
import re
import logging
from .nlp_parser import extract_contacts_nlp
from .vcard_parser import parse_vcard
from ..utils.nlp import categorize_contact

# Optional OCR imports - gracefully handle missing dependencies
try:
    import pytesseract
    from PIL import Image
    import os
    import shutil
    import subprocess

    def find_tesseract():
        """Find Tesseract executable in common locations"""
        # Try environment variable first
        env_path = os.getenv('TESSERACT_PATH')
        if env_path and os.path.isfile(env_path):
            return env_path

        # Common Tesseract paths to try
        common_paths = [
            '/usr/bin/tesseract',
            '/usr/local/bin/tesseract',
            '/opt/homebrew/bin/tesseract',  # macOS with Homebrew
            'tesseract',  # System PATH
        ]

        # Try using 'which' command
        try:
            result = subprocess.run(['which', 'tesseract'],
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except:
            pass

        # Try shutil.which (Python's built-in)
        which_result = shutil.which('tesseract')
        if which_result:
            return which_result

        # Try common paths
        for path in common_paths:
            if path != 'tesseract' and os.path.isfile(path):
                return path

        return None

    # Find and configure Tesseract
    tesseract_path = find_tesseract()

    if tesseract_path:
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
        print(f"🔧 Found Tesseract at: {tesseract_path}")

        # Set TESSDATA_PREFIX to use bundled tessdata
        # First, try to use bundled tessdata from the application directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        bundled_tessdata = os.path.join(script_dir, '..', '..', 'tessdata')
        bundled_tessdata = os.path.abspath(bundled_tessdata)

        tessdata_prefix = None

        # Check if bundled tessdata exists and has required files
        if os.path.isdir(bundled_tessdata) and os.path.isfile(os.path.join(bundled_tessdata, 'eng.traineddata')):
            tessdata_prefix = bundled_tessdata
            print(f"✅ Using bundled tessdata: {tessdata_prefix}")
        else:
            # Fallback to environment variable or system paths
            tessdata_prefix = os.getenv('TESSDATA_PREFIX')
            if not tessdata_prefix:
                # Try to find tessdata directory automatically
                common_paths = [
                    '/usr/share/tesseract-ocr/tessdata',
                    '/usr/share/tesseract-ocr/4.00/tessdata',
                    '/usr/share/tesseract-ocr/5.00/tessdata',
                    '/usr/share/tessdata',
                    '/usr/local/share/tessdata'
                ]

                for path in common_paths:
                    if os.path.isdir(path) and os.path.isfile(os.path.join(path, 'eng.traineddata')):
                        tessdata_prefix = path
                        print(f"🔍 Auto-detected system tessdata: {tessdata_prefix}")
                        break

        if tessdata_prefix:
            os.environ['TESSDATA_PREFIX'] = tessdata_prefix
            print(f"🔧 Set TESSDATA_PREFIX: {tessdata_prefix}")

            # Verify the eng.traineddata file exists
            eng_file = os.path.join(tessdata_prefix, 'eng.traineddata')
            if os.path.isfile(eng_file):
                print(f"✅ Found English language data: {eng_file}")
                # List all available language files
                try:
                    lang_files = [f for f in os.listdir(tessdata_prefix) if f.endswith('.traineddata')]
                    print(f"📋 Available languages: {', '.join([f.replace('.traineddata', '') for f in lang_files])}")
                except:
                    pass
            else:
                print(f"⚠️  English language data not found at: {eng_file}")
        else:
            print("⚠️  TESSDATA_PREFIX not set and could not auto-detect")

        # Test if tesseract is actually working
        try:
            version = pytesseract.get_tesseract_version()
            OCR_AVAILABLE = True
            print(f"✅ Tesseract OCR is available: {version}")
            if tessdata_prefix:
                print(f"✅ Using Tesseract data from: {tessdata_prefix}")
        except Exception as e:
            OCR_AVAILABLE = False
            print(f"⚠️  Tesseract found but not working: {e}")
            if tessdata_prefix:
                print(f"   Check TESSDATA_PREFIX: {tessdata_prefix}")
    else:
        OCR_AVAILABLE = False
        print("⚠️  Tesseract not found in common locations")
        print("   Checked paths: /usr/bin/tesseract, /usr/local/bin/tesseract, system PATH")
        print("   OCR functionality will be disabled")

except ImportError as e:
    OCR_AVAILABLE = False
    print(f"⚠️  OCR dependencies not available: {e}")
    print("   Install with: pip install pytesseract pillow")
    print("   Image parsing will be disabled")

logger = logging.getLogger(__name__)

def parse_pdf(file_content):
    doc = fitz.open(stream=file_content, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return extract_contacts(text)

def parse_docx(file_content):
    doc = Document(io.BytesIO(file_content))
    text = "\n".join([para.text for para in doc.paragraphs])
    return extract_contacts(text)

def parse_txt(file_content):
    text = file_content.decode("utf-8")

    # Check if this is structured data (tab-separated or CSV-like)
    lines = text.strip().split('\n')
    if len(lines) > 1:
        # Check if first line looks like headers
        first_line = lines[0].lower()
        if any(header in first_line for header in ['name', 'email', 'phone', 'company', 'designation']):
            # Detect delimiter
            if '\t' in lines[0]:
                return parse_structured_text(text, delimiter='\t')
            elif ',' in lines[0] and lines[0].count(',') > 2:
                return parse_structured_text(text, delimiter=',')

    # Fallback to regular text parsing
    return extract_contacts(text)

def parse_structured_text(text, delimiter='\t'):
    """Parse structured text data (tab-separated or CSV-like)"""
    lines = text.strip().split('\n')
    if len(lines) < 2:
        return []

    # Parse header row
    headers = [h.strip().lower() for h in lines[0].split(delimiter)]
    contacts = []

    # Create field mapping
    field_mapping = {
        'name': ['name', 'full name', 'contact name'],
        'designation': ['designation', 'title', 'position', 'job title'],
        'company': ['company', 'organization', 'org', 'business'],
        'phone': ['phone', 'telephone', 'tel', 'mobile', 'cell'],
        'email': ['email', 'e-mail', 'mail'],
        'website': ['website', 'web', 'url', 'site'],
        'category': ['category', 'type', 'classification'],
        'address': ['address', 'location', 'addr'],
        'notes': ['notes', 'note', 'comments', 'remarks', 'description']
    }

    # Find column indices for each field
    column_map = {}
    for field, possible_names in field_mapping.items():
        for i, header in enumerate(headers):
            if any(name in header for name in possible_names):
                column_map[field] = i
                break

    # Parse data rows
    for line_num, line in enumerate(lines[1:], 2):
        if not line.strip():
            continue

        try:
            values = line.split(delimiter)
            contact = {
                'name': '',
                'designation': '',
                'company': '',
                'phone': '',
                'email': '',
                'website': '',
                'category': 'Others',
                'address': '',
                'notes': ''
            }

            # Extract values based on column mapping
            for field, col_index in column_map.items():
                if col_index < len(values):
                    value = values[col_index].strip()
                    if value:
                        contact[field] = value

            # Apply intelligent categorization if category is not provided or is generic
            if not contact['category'] or contact['category'].lower() in ['others', 'uncategorized', '']:
                contact['category'] = categorize_contact(contact)

            # Only add contact if it has at least a name or email
            if contact['name'] or contact['email']:
                contacts.append(contact)

        except Exception as e:
            logger.warning(f"Error parsing line {line_num}: {e}")
            continue

    return contacts

def parse_vcf(file_content):
    """Parse vCard (.vcf) files"""
    try:
        text = file_content.decode("utf-8")
        logger.info("Parsing vCard file")
        return parse_vcard(text)
    except Exception as e:
        logger.error(f"Error parsing vCard file: {e}")
        return []

def parse_image(file_content):
    if not OCR_AVAILABLE:
        logger.warning("OCR not available. Cannot parse image files.")
        return []

    try:
        image = Image.open(io.BytesIO(file_content))
        text = pytesseract.image_to_string(image)
        return extract_contacts(text)
    except Exception as e:
        logger.error(f"Error parsing image: {e}")
        return []

def extract_contacts_icc_format(text):
    """Specialized parser for ICC contact data format"""
    contacts = []
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    # Enhanced patterns for ICC data
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    phone_pattern = r'(?:Tel|Phone|Fax|Mobile|Cell)?\s*(?:\+?91\s*)?(?:0\d{2,4}\s*)?(\d{8,12})'

    # Group lines by email (each email represents a new contact)
    contact_groups = []
    current_group = []

    for line in lines:
        if re.search(email_pattern, line):
            if current_group:
                contact_groups.append(current_group)
            current_group = [line]
        else:
            current_group.append(line)

    if current_group:
        contact_groups.append(current_group)

    # Process each group
    for group in contact_groups:
        contact = {
            "name": "",
            "email": "",
            "phone": "",
            "address": "",
            "category": "Work",  # ICC contacts are business contacts
            "notes": ""
        }

        tel_numbers = []
        fax_numbers = []
        address_parts = []

        for line in group:
            # Extract email
            emails = re.findall(email_pattern, line)
            if emails:
                contact["email"] = emails[0]
                # Extract city/location from email
                if 'icc_' in emails[0]:
                    city_code = emails[0].split('icc_')[1].split('@')[0]
                    city_mapping = {
                        'amd': 'Ahmedabad',
                        'chennai': 'Chennai',
                        'pune': 'Pune',
                        'baroda': 'Baroda/Vadodara',
                        'cjb': 'Coimbatore',
                        'delhi': 'Delhi',
                        'erode': 'Erode',
                        'hyd': 'Hyderabad',
                        'jaipur': 'Jaipur',
                        'karur': 'Karur',
                        'kolkata': 'Kolkata',
                        'tirupur': 'Tirupur',
                        'kanpur': 'Kanpur'
                    }
                    city = city_mapping.get(city_code, city_code.title())
                    contact["name"] = f"ICC {city}"
                continue

            # Extract phone numbers
            if line.lower().startswith('tel'):
                phones = re.findall(r'[\d\s]+', line)
                for phone in phones:
                    clean_phone = re.sub(r'\D', '', phone)
                    if len(clean_phone) >= 8:
                        tel_numbers.append(clean_phone)
                continue

            # Extract fax numbers
            if line.lower().startswith('fax'):
                phones = re.findall(r'[\d\s]+', line)
                for phone in phones:
                    clean_phone = re.sub(r'\D', '', phone)
                    if len(clean_phone) >= 8:
                        fax_numbers.append(clean_phone)
                continue

            # Address components
            if (any(keyword in line.lower() for keyword in ['road', 'street', 'lane', 'building', 'floor', 'complex', 'center', 'house', 'near']) or
                re.match(r'^[A-Z]?/?[\d-]+[A-Z]?$', line.strip()) or
                any(city in line for city in ['India', 'Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata', 'Pune', 'Hyderabad', 'Ahmedabad'])):
                address_parts.append(line)

        # Set phone (prefer tel over fax)
        if tel_numbers:
            contact["phone"] = tel_numbers[0]
        elif fax_numbers:
            contact["phone"] = fax_numbers[0]

        # Set address
        contact["address"] = ", ".join(address_parts) if address_parts else ""

        # Add fax to notes if different from phone
        if fax_numbers and (not tel_numbers or fax_numbers[0] != tel_numbers[0]):
            contact["notes"] = f"Fax: {fax_numbers[0]}"

        # Only add if we have meaningful data
        if contact["email"] or contact["phone"]:
            if not contact["name"]:
                contact["name"] = "ICC Office"
            contacts.append(contact)

    return contacts

def extract_contacts(text):
    """Enhanced contact extraction with intelligent grouping and pattern matching"""
    # Check if this looks like ICC format data
    if 'icc_' in text.lower() and '@iccworld.com' in text.lower():
        return extract_contacts_icc_format(text)

    # Try NLP-based extraction for unstructured text
    try:
        nlp_contacts = extract_contacts_nlp(text)
        if nlp_contacts and len(nlp_contacts) > 0:
            logger.info(f"NLP parser extracted {len(nlp_contacts)} contacts")
            return nlp_contacts
    except Exception as e:
        logger.warning(f"NLP parsing failed: {e}, falling back to regex parser")

    # Original general parser for other formats
    contacts = []
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    # Enhanced patterns
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    phone_pattern = r'(?:Tel|Phone|Fax|Mobile|Cell)?\s*(?:\+?91\s*)?(?:0\d{2,4}\s*)?(\d{8,12})'
    address_keywords = ['road', 'street', 'avenue', 'lane', 'building', 'floor', 'suite', 'apartment', 'house', 'complex', 'center', 'plaza', 'tower', 'near', 'opp', 'opposite']

    # Group related lines together
    contact_groups = []
    current_group = []

    for i, line in enumerate(lines):
        # Check if this line starts a new contact group
        if (re.search(email_pattern, line) or
            any(keyword in line.lower() for keyword in ['email', 'tel', 'phone', 'fax']) or
            (i > 0 and line and not line[0].isdigit() and not line.startswith(('Tel', 'Fax', 'Email')))):

            if current_group:
                contact_groups.append(current_group)
                current_group = []

        current_group.append(line)

    if current_group:
        contact_groups.append(current_group)

    # Process each group to extract contact information
    for group in contact_groups:
        contact = {
            "name": "",
            "email": "",
            "phone": "",
            "address": "",
            "category": "Uncategorized",
            "notes": ""
        }

        address_parts = []
        notes_parts = []

        for line in group:
            # Extract email
            emails = re.findall(email_pattern, line)
            if emails:
                contact["email"] = emails[0]
                continue

            # Extract phone numbers
            phones = re.findall(phone_pattern, line)
            if phones and not contact["phone"]:
                # Clean and format phone number
                phone = re.sub(r'\D', '', phones[0])
                if len(phone) >= 8:
                    contact["phone"] = phone[-10:] if len(phone) > 10 else phone
                continue

            # Check if line contains address information
            if any(keyword in line.lower() for keyword in address_keywords):
                address_parts.append(line)
                continue

            # Check for location/city information
            if any(keyword in line.lower() for keyword in ['india', 'mumbai', 'delhi', 'bangalore', 'chennai', 'kolkata', 'pune', 'hyderabad']):
                address_parts.append(line)
                continue

            # If line contains building/office identifiers
            if re.match(r'^[A-Z]?/?[\d-]+[A-Z]?$', line.strip()) or line.strip().endswith(('Floor', 'floor')):
                address_parts.append(line)
                continue

            # Extract name (usually the first meaningful line that's not tel/email/address)
            if (not contact["name"] and
                not line.lower().startswith(('tel', 'fax', 'email', 'phone')) and
                not re.match(r'^\d+$', line.strip()) and
                len(line.split()) >= 2):
                contact["name"] = line.strip()
                continue

            # Everything else goes to notes
            if line and not re.match(r'^\d+$', line.strip()):
                notes_parts.append(line)

        # Compile address and notes
        contact["address"] = ", ".join(address_parts) if address_parts else ""
        contact["notes"] = ", ".join(notes_parts) if notes_parts else ""

        # Only add contact if we have at least a name, email, or phone
        if contact["name"] or contact["email"] or contact["phone"]:
            # If no name but have email, extract name from email
            if not contact["name"] and contact["email"]:
                email_name = contact["email"].split('@')[0].replace('.', ' ').replace('_', ' ')
                contact["name"] = email_name.title()

            # If still no name, create one from available info
            if not contact["name"]:
                if contact["phone"]:
                    contact["name"] = f"Contact {contact['phone'][-4:]}"
                else:
                    contact["name"] = "Unknown Contact"

            contacts.append(contact)

    return contacts