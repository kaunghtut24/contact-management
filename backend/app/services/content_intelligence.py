"""
Content Intelligence Service
Combines LLM and SpaCy for intelligent content detection and extraction across all file types
"""
import os
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple
import re
from datetime import datetime

logger = logging.getLogger(__name__)

# Optional imports with graceful fallback
try:
    import spacy
    from spacy.matcher import Matcher
    SPACY_AVAILABLE = True
    logger.info("✅ SpaCy available")
except ImportError:
    SPACY_AVAILABLE = False
    logger.warning("⚠️ SpaCy not available")

try:
    import openai
    LLM_AVAILABLE = True
    logger.info("✅ OpenAI client available")
except ImportError:
    LLM_AVAILABLE = False
    logger.warning("⚠️ OpenAI client not available")

class ContentIntelligenceService:
    """
    Advanced content intelligence combining LLM and SpaCy for accurate contact extraction
    """
    
    def __init__(self):
        self.spacy_model = None
        self.matcher = None
        self.llm_clients = {}
        self.providers = {}  # Alias for compatibility
        self.default_provider = None
        self.business_categories = [
            "Government", "Embassy", "Consulate", "High Commissioner",
            "Deputy High Commissioner", "Associations", "Exporter", "Importer",
            "Logistics", "Event management", "Consultancy", "Manufacturer",
            "Distributors", "Producers", "Others"
        ]

        self._initialize_spacy()
        self._initialize_llm_clients()
    
    def _initialize_spacy(self):
        """Initialize SpaCy model and custom matchers"""
        if not SPACY_AVAILABLE:
            logger.warning("SpaCy not available, using rule-based extraction only")
            return
        
        try:
            # Try to load the model
            model_name = os.getenv("SPACY_MODEL", "en_core_web_sm")
            self.spacy_model = spacy.load(model_name)
            self.matcher = Matcher(self.spacy_model.vocab)
            
            # Add custom patterns for business entities
            self._add_business_patterns()
            logger.info(f"✅ SpaCy model '{model_name}' loaded successfully")
            
        except OSError as e:
            logger.warning(f"⚠️ SpaCy model not found: {e}")
            self.spacy_model = None
            self.matcher = None
    
    def _add_business_patterns(self):
        """Add custom patterns for business entity recognition"""
        if not self.matcher:
            logger.warning("⚠️ Matcher not available, skipping pattern addition")
            return

        try:
            # Designation patterns
            designation_patterns = [
                [{"LOWER": {"IN": ["ceo", "chief", "executive", "officer"]}}],
                [{"LOWER": {"IN": ["manager", "director", "president", "vice"]}}],
                [{"LOWER": {"IN": ["ambassador", "consul", "commissioner"]}}],
                [{"LOWER": "senior"}, {"LOWER": {"IN": ["manager", "director", "engineer"]}}],
                [{"LOWER": "deputy"}, {"LOWER": {"IN": ["commissioner", "director"]}}],
            ]

            # Company type patterns
            company_patterns = [
                [{"LOWER": {"IN": ["ltd", "limited", "inc", "incorporated", "corp", "corporation"]}}],
                [{"LOWER": {"IN": ["embassy", "consulate", "ministry", "department"]}}],
                [{"LOWER": "co"}, {"LOWER": "ltd"}],
                [{"LOWER": {"IN": ["llc", "llp", "plc"]}}],
            ]

            # Email patterns (additional validation)
            email_patterns = [
                [{"LIKE_EMAIL": True}],
            ]

            # Phone patterns
            phone_patterns = [
                [{"SHAPE": "ddd-ddd-dddd"}],
                [{"SHAPE": "(ddd) ddd-dddd"}],
                [{"TEXT": {"REGEX": r"^\+?[\d\s\-\(\)]{8,15}$"}}],
            ]

            # Add patterns to matcher with error handling
            try:
                self.matcher.add("DESIGNATION", designation_patterns)
                logger.debug("✅ Added designation patterns")
            except Exception as e:
                logger.warning(f"⚠️ Failed to add designation patterns: {e}")

            try:
                self.matcher.add("COMPANY_TYPE", company_patterns)
                logger.debug("✅ Added company type patterns")
            except Exception as e:
                logger.warning(f"⚠️ Failed to add company type patterns: {e}")

            try:
                self.matcher.add("EMAIL_PATTERN", email_patterns)
                logger.debug("✅ Added email patterns")
            except Exception as e:
                logger.warning(f"⚠️ Failed to add email patterns: {e}")

            logger.info(f"✅ Added {len(self.matcher)} custom patterns to SpaCy matcher")

        except Exception as e:
            logger.error(f"❌ Failed to add business patterns: {e}")
            # Create a minimal matcher to avoid warnings
            try:
                simple_pattern = [[{"LOWER": "email"}]]
                self.matcher.add("SIMPLE", simple_pattern)
                logger.info("✅ Added minimal pattern to avoid matcher warnings")
            except:
                logger.warning("⚠️ Could not add even simple patterns to matcher")
    
    def _initialize_llm_clients(self):
        """Initialize multiple LLM clients"""
        logger.info("🔧 Initializing LLM clients...")

        # OpenAI (or OpenAI-compatible)
        openai_key = os.getenv("OPENAI_API_KEY")
        logger.debug(f"OpenAI API key present: {bool(openai_key)}")

        if openai_key and LLM_AVAILABLE:
            try:
                base_url = os.getenv("OPENAI_BASE_URL")
                self.llm_clients["openai"] = {
                    "client": openai.OpenAI(api_key=openai_key, base_url=base_url),
                    "model": os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                    "type": "openai"
                }
                self.providers["openai"] = self.llm_clients["openai"]  # Alias
                if not self.default_provider:
                    self.default_provider = "openai"
                logger.info("✅ OpenAI client initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize OpenAI client: {e}")

        # Add Groq provider
        groq_key = os.getenv("GROQ_API_KEY")
        logger.debug(f"Groq API key present: {bool(groq_key)}")

        if groq_key and LLM_AVAILABLE:
            try:
                self.llm_clients["groq"] = {
                    "client": openai.OpenAI(
                        api_key=groq_key,
                        base_url="https://api.groq.com/openai/v1"
                    ),
                    "model": os.getenv("GROQ_MODEL", "mixtral-8x7b-32768"),
                    "type": "openai_compatible"
                }
                self.providers["groq"] = self.llm_clients["groq"]  # Alias
                if not self.default_provider:
                    self.default_provider = "groq"
                logger.info("✅ Groq client initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Groq client: {e}")

        if not self.llm_clients:
            logger.warning("⚠️ No LLM clients configured - using SpaCy fallback only")
            self.default_provider = None
        else:
            logger.info(f"🤖 Default LLM provider: {self.default_provider}")
            logger.info(f"📊 Available providers: {list(self.providers.keys())}")

        # Log environment variables for debugging
        logger.debug(f"Environment check - OPENAI_API_KEY: {bool(os.getenv('OPENAI_API_KEY'))}")
        logger.debug(f"Environment check - GROQ_API_KEY: {bool(os.getenv('GROQ_API_KEY'))}")
    
    async def analyze_content(self, text: str, file_type: str = "unknown") -> Dict[str, Any]:
        """
        Comprehensive content analysis using both SpaCy and LLM
        """
        logger.info(f"Analyzing {len(text)} characters of {file_type} content")
        
        # Step 1: SpaCy-based entity extraction
        spacy_results = self._extract_with_spacy(text)
        
        # Step 2: LLM-based intelligent extraction
        llm_results = await self._extract_with_llm(text, file_type, spacy_results)
        
        # Step 3: Combine and validate results
        combined_results = self._combine_results(spacy_results, llm_results, text)
        
        return {
            "success": True,
            "file_type": file_type,
            "analysis": {
                "spacy_entities": spacy_results,
                "llm_extraction": llm_results,
                "combined_contacts": combined_results["contacts"],
                "confidence_score": combined_results["confidence"],
                "processing_method": combined_results["method"]
            },
            "contacts": combined_results["contacts"],
            "metadata": {
                "text_length": len(text),
                "entities_found": len(spacy_results.get("entities", [])),
                "contacts_extracted": len(combined_results["contacts"]),
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    
    def _extract_with_spacy(self, text: str) -> Dict[str, Any]:
        """Extract entities using SpaCy NLP"""
        if not self.spacy_model:
            return {"entities": [], "method": "rule_based"}
        
        try:
            doc = self.spacy_model(text)
            
            entities = {
                "PERSON": [],
                "ORG": [],
                "EMAIL": [],
                "PHONE": [],
                "GPE": [],  # Geopolitical entities (countries, cities)
                "CUSTOM": []
            }
            
            # Extract named entities
            for ent in doc.ents:
                if ent.label_ in entities:
                    entities[ent.label_].append({
                        "text": ent.text,
                        "start": ent.start_char,
                        "end": ent.end_char,
                        "confidence": 0.8  # SpaCy confidence approximation
                    })
            
            # Extract custom patterns (with error handling)
            try:
                if self.matcher and len(self.matcher) > 0:
                    matches = self.matcher(doc)
                    for match_id, start, end in matches:
                        span = doc[start:end]
                        label = self.spacy_model.vocab.strings[match_id]
                        entities["CUSTOM"].append({
                            "text": span.text,
                            "label": label,
                            "start": span.start_char,
                            "end": span.end_char
                        })
                else:
                    logger.debug("⚠️ Matcher has no patterns, skipping custom pattern extraction")
            except Exception as e:
                logger.warning(f"⚠️ Custom pattern matching failed: {e}")
            
            # Extract emails and phones with regex (more reliable)
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            phone_pattern = r'[\+]?[1-9][\d\s\-\(\)]{7,14}'  # More precise phone pattern
            
            for match in re.finditer(email_pattern, text, re.IGNORECASE):
                entities["EMAIL"].append({
                    "text": match.group(),
                    "start": match.start(),
                    "end": match.end(),
                    "confidence": 0.9
                })
            
            for match in re.finditer(phone_pattern, text):
                phone_text = match.group().strip()
                if len(phone_text) >= 8:  # Ensure minimum phone length
                    entities["PHONE"].append({
                        "text": phone_text,
                        "start": match.start(),
                        "end": match.end(),
                        "confidence": 0.7
                    })
            
            return {
                "entities": entities,
                "method": "spacy_nlp",
                "model": self.spacy_model.meta.get("name", "unknown")
            }
            
        except Exception as e:
            logger.warning(f"SpaCy extraction failed: {e}")
            return {"entities": [], "method": "spacy_failed", "error": str(e)}
    
    async def _extract_with_llm(self, text: str, file_type: str, spacy_results: Dict) -> Dict[str, Any]:
        """Extract contacts using LLM with SpaCy context"""
        if not self.llm_clients:
            return {"contacts": [], "method": "no_llm"}
        
        # Use the first available LLM client
        client_name = list(self.llm_clients.keys())[0]
        client_config = self.llm_clients[client_name]
        
        try:
            # Create enhanced prompt with SpaCy context
            prompt = self._create_enhanced_prompt(text, file_type, spacy_results)
            logger.debug(f"LLM prompt length: {len(prompt)}")
            logger.debug(f"LLM prompt preview: {prompt[:300]}...")

            logger.info(f"🤖 Calling {client_name} ({client_config['model']}) for contact extraction")

            response = await asyncio.to_thread(
                client_config["client"].chat.completions.create,
                model=client_config["model"],
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.1
            )

            result_text = response.choices[0].message.content
            logger.info(f"📝 LLM response received, length: {len(result_text) if result_text else 0}")

            # Check for empty or None response
            if not result_text or not result_text.strip():
                logger.warning(f"LLM ({client_name}) returned empty response")
                raise ValueError("Empty response from LLM")

            result_text = result_text.strip()
            logger.debug(f"LLM ({client_name}) response: {result_text[:200]}...")

            # Parse JSON response with improved error handling
            try:
                # Clean the response text
                cleaned_text = result_text.strip()

                # Try direct JSON parsing first
                contacts = json.loads(cleaned_text)
                return {
                    "contacts": contacts,
                    "method": f"llm_{client_name}",
                    "model": client_config["model"]
                }
            except json.JSONDecodeError:
                logger.warning(f"Direct JSON parsing failed, trying extraction. Response: {result_text[:200]}...")

                # Try to extract JSON array from response
                json_patterns = [
                    r'\[[\s\S]*?\]',  # Match array with any content
                    r'```json\s*(\[[\s\S]*?\])\s*```',  # Match JSON in code blocks
                    r'```\s*(\[[\s\S]*?\])\s*```',  # Match array in any code blocks
                ]

                for pattern in json_patterns:
                    json_match = re.search(pattern, result_text, re.DOTALL)
                    if json_match:
                        try:
                            json_text = json_match.group(1) if json_match.groups() else json_match.group(0)
                            contacts = json.loads(json_text)
                            logger.info(f"Successfully extracted JSON using pattern: {pattern}")
                            return {
                                "contacts": contacts,
                                "method": f"llm_{client_name}_extracted",
                                "model": client_config["model"]
                            }
                        except json.JSONDecodeError:
                            continue

                # If all JSON extraction fails, create a basic contact from the text
                logger.warning(f"All JSON extraction failed. Full response: {result_text}")
                logger.info("Creating fallback contact from LLM response text")

                # Extract basic info from the response text
                fallback_contact = self._create_fallback_contact_from_text(result_text, spacy_results)
                return {
                    "contacts": [fallback_contact] if fallback_contact else [],
                    "method": f"llm_{client_name}_fallback",
                    "model": client_config["model"]
                }
            
        except Exception as e:
            logger.error(f"LLM extraction failed with {client_name}: {e}")
            logger.debug(f"LLM prompt was: {prompt[:200]}...")
            return {"contacts": [], "method": "llm_failed", "error": str(e), "client": client_name}
    
    def _create_enhanced_prompt(self, text: str, file_type: str, spacy_results: Dict) -> str:
        """Create enhanced prompt using SpaCy context"""
        entities = spacy_results.get("entities", {})
        
        # Extract key entities for context
        persons = [e["text"] for e in entities.get("PERSON", [])]
        orgs = [e["text"] for e in entities.get("ORG", [])]
        emails = [e["text"] for e in entities.get("EMAIL", [])]
        phones = [e["text"] for e in entities.get("PHONE", [])]
        
        context = f"""
File Type: {file_type}
SpaCy Analysis Context:
- Persons detected: {persons[:5]}  # Limit to first 5
- Organizations: {orgs[:5]}
- Emails found: {emails}
- Phones found: {phones}
"""
        
        return f"""Extract contact information and return ONLY valid JSON array.

{context}

STRICT RULES:
1. Return ONLY JSON array - no other text, explanations, or formatting
2. Each contact needs: name, designation, company, email, phone, website, address, categories
3. Use "" for empty fields
4. Categories from: {self.business_categories}
5. Categories must be array: ["category1", "category2"]

EXAMPLE OUTPUT:
[{{"name":"John Doe","designation":"Manager","company":"ABC Corp","email":"john@abc.com","phone":"+1234567890","website":"","address":"123 Main St","categories":["Others"]}}]

TEXT:
{text}

JSON:"""

    def _combine_results(self, spacy_results: Dict, llm_results: Dict, original_text: str) -> Dict[str, Any]:
        """Combine SpaCy and LLM results for optimal accuracy"""

        # Get contacts from LLM
        llm_contacts = llm_results.get("contacts", [])

        # Get entities from SpaCy
        entities = spacy_results.get("entities", {})

        if not llm_contacts:
            # Fallback to SpaCy-based extraction
            return self._create_contacts_from_spacy(entities, original_text)

        # Enhance LLM contacts with SpaCy validation
        enhanced_contacts = []

        for contact in llm_contacts:
            enhanced_contact = self._validate_and_enhance_contact(contact, entities, original_text)
            if enhanced_contact:
                enhanced_contacts.append(enhanced_contact)

        # Calculate confidence score
        confidence = self._calculate_confidence(enhanced_contacts, entities)

        return {
            "contacts": enhanced_contacts,
            "confidence": confidence,
            "method": "combined_spacy_llm"
        }

    def _validate_and_enhance_contact(self, contact: Dict, entities: Dict, text: str) -> Optional[Dict]:
        """Validate and enhance a contact using SpaCy entities"""

        # Validate required fields
        required_fields = ["name", "designation", "company", "email", "phone", "website", "address", "categories"]
        for field in required_fields:
            if field not in contact:
                contact[field] = ""

        # Validate email
        if contact["email"]:
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            if not re.match(email_pattern, contact["email"]):
                # Try to find a valid email in SpaCy results
                spacy_emails = [e["text"] for e in entities.get("EMAIL", [])]
                if spacy_emails:
                    contact["email"] = spacy_emails[0]
                else:
                    contact["email"] = ""

        # Validate phone
        if contact["phone"]:
            # Clean phone number
            contact["phone"] = re.sub(r'[^\d\+\-\(\)\s]', '', contact["phone"])

        # Validate categories
        if isinstance(contact["categories"], str):
            contact["categories"] = [contact["categories"]]

        valid_categories = []
        for cat in contact.get("categories", []):
            if cat in self.business_categories:
                valid_categories.append(cat)

        if not valid_categories:
            # Try to infer category from company name or designation
            inferred_category = self._infer_category(contact, text)
            valid_categories = [inferred_category]

        contact["categories"] = valid_categories

        # Enhance with SpaCy entities if fields are missing
        if not contact["name"] and entities.get("PERSON"):
            contact["name"] = entities["PERSON"][0]["text"]

        if not contact["company"] and entities.get("ORG"):
            contact["company"] = entities["ORG"][0]["text"]

        return contact

    def _infer_category(self, contact: Dict, text: str) -> str:
        """Infer business category from contact information"""

        # Category keywords mapping
        category_keywords = {
            "Government": ["government", "ministry", "department", "public", "state", "federal"],
            "Embassy": ["embassy", "ambassador", "diplomatic", "consular"],
            "Consulate": ["consulate", "consul", "vice consul"],
            "High Commissioner": ["high commissioner", "high commission"],
            "Deputy High Commissioner": ["deputy high commissioner", "deputy commission"],
            "Associations": ["association", "society", "union", "federation", "chamber"],
            "Exporter": ["export", "exporter", "international trade", "overseas"],
            "Importer": ["import", "importer", "trading", "distribution"],
            "Logistics": ["logistics", "shipping", "freight", "cargo", "transport"],
            "Event management": ["event", "conference", "exhibition", "management", "organizing"],
            "Consultancy": ["consultant", "consulting", "advisory", "services"],
            "Manufacturer": ["manufacturer", "manufacturing", "factory", "production"],
            "Distributors": ["distributor", "distribution", "wholesale", "supply"],
            "Producers": ["producer", "production", "maker", "creator"]
        }

        # Check company name and designation
        search_text = f"{contact.get('company', '')} {contact.get('designation', '')}".lower()

        for category, keywords in category_keywords.items():
            if any(keyword in search_text for keyword in keywords):
                return category

        # Check in full text context
        text_lower = text.lower()
        for category, keywords in category_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return category

        return "Others"

    def _create_contacts_from_spacy(self, entities: Dict, text: str) -> Dict[str, Any]:
        """Create contacts from SpaCy entities when LLM fails"""

        emails = [e["text"] for e in entities.get("EMAIL", [])]
        phones = [e["text"] for e in entities.get("PHONE", [])]
        persons = [e["text"] for e in entities.get("PERSON", [])]
        orgs = [e["text"] for e in entities.get("ORG", [])]

        contacts = []

        # Create one contact per email found
        for i, email in enumerate(emails):
            contact = {
                "name": persons[i] if i < len(persons) else "",
                "designation": "",
                "company": orgs[i] if i < len(orgs) else (orgs[0] if orgs else ""),
                "email": email,
                "phone": phones[i] if i < len(phones) else (phones[0] if phones else ""),
                "website": "",
                "address": "",
                "categories": [self._infer_category({"company": orgs[0] if orgs else "", "designation": ""}, text)]
            }
            contacts.append(contact)

        # If no emails, create one contact with available info
        if not contacts and (persons or orgs or phones):
            contact = {
                "name": persons[0] if persons else "",
                "designation": "",
                "company": orgs[0] if orgs else "",
                "email": "",
                "phone": phones[0] if phones else "",
                "website": "",
                "address": "",
                "categories": [self._infer_category({"company": orgs[0] if orgs else "", "designation": ""}, text)]
            }
            contacts.append(contact)

        return {
            "contacts": contacts,
            "confidence": 0.6,  # Lower confidence for SpaCy-only
            "method": "spacy_fallback"
        }

    def _calculate_confidence(self, contacts: List[Dict], entities: Dict) -> float:
        """Calculate confidence score for extracted contacts"""

        if not contacts:
            return 0.0

        total_score = 0
        for contact in contacts:
            score = 0

            # Score based on filled fields
            if contact.get("name"): score += 0.2
            if contact.get("email") and "@" in contact["email"]: score += 0.3
            if contact.get("phone"): score += 0.2
            if contact.get("company"): score += 0.2
            if contact.get("categories") and contact["categories"] != ["Others"]: score += 0.1

            total_score += score

        # Average score across contacts
        avg_score = total_score / len(contacts)

        # Boost if SpaCy entities support the extraction
        entity_boost = 0
        if entities.get("EMAIL"): entity_boost += 0.1
        if entities.get("PERSON"): entity_boost += 0.1
        if entities.get("ORG"): entity_boost += 0.1

        return min(1.0, avg_score + entity_boost)

    def _create_fallback_contact_from_text(self, llm_text: str, spacy_results: Dict) -> Optional[Dict]:
        """Create a basic contact when LLM returns invalid JSON but useful text"""
        try:
            # Get entities from SpaCy
            entities = spacy_results.get("entities", {})

            # Extract basic info from LLM text and SpaCy entities
            contact = {
                "name": "",
                "designation": "",
                "company": "",
                "email": "",
                "phone": "",
                "website": "",
                "address": "",
                "categories": ["Others"]
            }

            # Use SpaCy entities as primary source
            if entities.get("EMAIL"):
                contact["email"] = entities["EMAIL"][0]["text"]
            if entities.get("PHONE"):
                contact["phone"] = entities["PHONE"][0]["text"]
            if entities.get("PERSON"):
                contact["name"] = entities["PERSON"][0]["text"]
            if entities.get("ORG"):
                contact["company"] = entities["ORG"][0]["text"]

            # Try to extract additional info from LLM text
            lines = llm_text.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Look for email if not found
                if not contact["email"] and '@' in line:
                    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', line, re.IGNORECASE)
                    if email_match:
                        contact["email"] = email_match.group()

                # Look for phone if not found
                if not contact["phone"] and any(char.isdigit() for char in line):
                    phone_match = re.search(r'[\+]?[1-9][\d\s\-\(\)]{7,14}', line)
                    if phone_match:
                        contact["phone"] = phone_match.group().strip()

                # Look for name if not found (lines with proper case, no special chars)
                if not contact["name"] and len(line.split()) <= 3 and line.replace(' ', '').isalpha():
                    if line[0].isupper():  # Likely a name
                        contact["name"] = line

            # Only return contact if we have at least email or phone
            if contact["email"] or contact["phone"] or contact["name"]:
                logger.info(f"Created fallback contact: {contact['name']} - {contact['email']}")
                return contact

            return None

        except Exception as e:
            logger.error(f"Fallback contact creation failed: {e}")
            return None

# Global instance
content_intelligence = ContentIntelligenceService()
