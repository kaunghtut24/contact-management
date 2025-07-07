def categorize_contact(contact):
    """Enhanced contact categorization with specialized categories"""
    if isinstance(contact, dict):
        name = contact.get("name", "").lower()
        designation = contact.get("designation", "").lower()
        company = contact.get("company", "").lower()
        telephone = contact.get("telephone", "").lower()
        email = contact.get("email", "").lower()
        website = contact.get("website", "").lower()
        notes = contact.get("notes", "").lower()
        # Legacy fields
        phone = contact.get("phone", "").lower()
        address = contact.get("address", "").lower()
    else:
        name = getattr(contact, "name", "") or ""
        designation = getattr(contact, "designation", "") or ""
        company = getattr(contact, "company", "") or ""
        telephone = getattr(contact, "telephone", "") or ""
        email = getattr(contact, "email", "") or ""
        website = getattr(contact, "website", "") or ""
        notes = getattr(contact, "notes", "") or ""
        # Legacy fields
        phone = getattr(contact, "phone", "") or ""
        address = getattr(contact, "address", "") or ""

    # Combine all text for analysis (prioritize new fields)
    all_text = f"{name} {designation} {company} {telephone} {email} {website} {notes} {phone} {address}".lower()

    # Priority-based categorization (most specific first)

    # 1. Government & Diplomatic Categories
    government_keywords = [
        'government', 'ministry', 'minister', 'secretary', 'department', 'bureau',
        'administration', 'authority', 'commission', 'council', 'municipal',
        'federal', 'state', 'provincial', 'district', 'county', 'city hall',
        'public', 'official', 'civil service', 'bureaucrat', 'commissioner'
    ]

    embassy_keywords = [
        'embassy', 'embassies', 'ambassador', 'ambassadorial', 'diplomatic mission',
        'diplomatic', 'foreign ministry', 'foreign affairs', 'external affairs'
    ]

    consulate_keywords = [
        'consulate', 'consular', 'consul', 'vice consul', 'consul general',
        'consular services', 'visa office', 'passport office'
    ]

    high_commissioner_keywords = [
        'high commissioner', 'high commission', 'deputy high commissioner',
        'assistant high commissioner', 'commonwealth', 'british high commission'
    ]

    # 2. Business & Trade Categories
    association_keywords = [
        'association', 'chamber', 'federation', 'union', 'society', 'institute',
        'foundation', 'organization', 'club', 'guild', 'alliance', 'consortium',
        'cooperative', 'network', 'forum', 'council', 'board', 'committee'
    ]

    exporter_keywords = [
        'export', 'exporter', 'exports', 'international trade', 'overseas',
        'foreign trade', 'global trade', 'shipping', 'freight forwarder',
        'trade house', 'merchant exporter', 'export house'
    ]

    importer_keywords = [
        'import', 'importer', 'imports', 'importing', 'procurement',
        'sourcing', 'purchasing', 'buying house', 'import house'
    ]

    logistics_keywords = [
        'logistics', 'supply chain', 'warehouse', 'distribution', 'transport',
        'transportation', 'shipping', 'freight', 'cargo', 'courier',
        'delivery', 'fulfillment', 'storage', '3pl', 'third party logistics'
    ]

    event_management_keywords = [
        'event', 'events', 'event management', 'conference', 'exhibition',
        'trade show', 'expo', 'fair', 'convention', 'seminar', 'workshop',
        'meeting', 'organizer', 'planner', 'coordinator', 'venue'
    ]

    # 3. New Business Categories
    consultancy_keywords = [
        'consultancy', 'consultant', 'consulting', 'advisory', 'advisor',
        'consulting firm', 'consultants', 'advisory services', 'consulting services',
        'management consulting', 'business consulting', 'technical consulting'
    ]

    manufacturer_keywords = [
        'manufacturer', 'manufacturing', 'factory', 'production', 'producer',
        'industrial', 'plant', 'mill', 'fabrication', 'assembly', 'maker',
        'manufacturing company', 'production facility', 'industrial unit'
    ]

    distributor_keywords = [
        'distributor', 'distribution', 'wholesale', 'wholesaler', 'dealer',
        'reseller', 'retailer', 'supplier', 'vendor', 'stockist',
        'distribution center', 'supply chain', 'channel partner'
    ]

    producer_keywords = [
        'producer', 'production', 'producer company', 'content producer',
        'media producer', 'film producer', 'music producer', 'agricultural producer',
        'food producer', 'energy producer', 'oil producer'
    ]

    # 4. Additional Categories
    healthcare_keywords = [
        'hospital', 'clinic', 'medical', 'doctor', 'physician', 'nurse',
        'healthcare', 'health', 'pharmacy', 'laboratory', 'diagnostic'
    ]

    education_keywords = [
        'school', 'university', 'college', 'institute', 'academy', 'education',
        'training', 'learning', 'teacher', 'professor', 'student'
    ]

    finance_keywords = [
        'bank', 'banking', 'finance', 'financial', 'insurance', 'investment',
        'accounting', 'audit', 'tax', 'credit', 'loan', 'mortgage'
    ]

    # 4. General Categories
    personal_keywords = [
        'home', 'personal', 'friend', 'family', 'neighbor', 'buddy', 'mate',
        'college', 'school', 'university', 'gym', 'club', 'hobby', 'social',
        'residential', 'apartment', 'house', 'street', 'lane', 'avenue',
        'sister', 'brother', 'cousin', 'relative', 'gmail', 'yahoo', 'hotmail'
    ]

    # Priority-based categorization logic
    # Check most specific categories first

    # Diplomatic & Government (Highest Priority)
    if any(keyword in all_text for keyword in high_commissioner_keywords):
        return "High Commissioner"
    elif any(keyword in all_text for keyword in embassy_keywords):
        return "Embassy"
    elif any(keyword in all_text for keyword in consulate_keywords):
        return "Consulate"
    elif any(keyword in all_text for keyword in government_keywords):
        return "Government"

    # Business & Trade Categories
    elif any(keyword in all_text for keyword in association_keywords):
        return "Association"
    elif any(keyword in all_text for keyword in exporter_keywords):
        return "Exporter"
    elif any(keyword in all_text for keyword in importer_keywords):
        return "Importer"
    elif any(keyword in all_text for keyword in logistics_keywords):
        return "Logistics"
    elif any(keyword in all_text for keyword in event_management_keywords):
        return "Event Management"
    elif any(keyword in all_text for keyword in consultancy_keywords):
        return "Consultancy"
    elif any(keyword in all_text for keyword in manufacturer_keywords):
        return "Manufacturer"
    elif any(keyword in all_text for keyword in distributor_keywords):
        return "Distributor"
    elif any(keyword in all_text for keyword in producer_keywords):
        return "Producer"

    # Specialized Service Categories
    elif any(keyword in all_text for keyword in healthcare_keywords):
        return "Healthcare"
    elif any(keyword in all_text for keyword in education_keywords):
        return "Education"
    elif any(keyword in all_text for keyword in finance_keywords):
        return "Finance"

    # Email domain analysis for general categories
    elif email:
        domain = email.split('@')[-1] if '@' in email else ''
        if any(gov_domain in domain for gov_domain in ['.gov', 'government', 'ministry']):
            return "Government"
        elif any(edu_domain in domain for edu_domain in ['.edu', '.ac.', 'university', 'college']):
            return "Education"
        elif any(personal_domain in domain for personal_domain in ['gmail', 'yahoo', 'hotmail', 'outlook']):
            return "Personal"
        elif any(biz_domain in domain for biz_domain in ['company', 'corp', 'business', 'enterprise', '.org']):
            return "Business"

    # Personal category check
    elif any(keyword in all_text for keyword in personal_keywords):
        return "Personal"

    # Default fallback
    else:
        return "Others"