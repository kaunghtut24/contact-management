"""
Machine Learning-based contact categorization with user feedback learning
"""
import os
import pickle
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class MLContactCategorizer:
    def __init__(self, model_path: str = "models/contact_categorizer.pkl"):
        self.model_path = Path(model_path)
        self.model = None
        self.vectorizer = None
        self.label_encoder = None
        self.feedback_data = []
        self._load_model()
    
    def _load_model(self):
        """Load the trained model if it exists"""
        try:
            if self.model_path.exists():
                with open(self.model_path, 'rb') as f:
                    model_data = pickle.load(f)
                    self.model = model_data.get('model')
                    self.vectorizer = model_data.get('vectorizer')
                    self.label_encoder = model_data.get('label_encoder')
                    self.feedback_data = model_data.get('feedback_data', [])
                logger.info("ML categorization model loaded successfully")
            else:
                logger.info("No existing model found, will use rule-based categorization")
        except Exception as e:
            logger.warning(f"Error loading ML model: {e}")
            self.model = None
    
    def _save_model(self):
        """Save the trained model"""
        try:
            # Create models directory if it doesn't exist
            self.model_path.parent.mkdir(parents=True, exist_ok=True)
            
            model_data = {
                'model': self.model,
                'vectorizer': self.vectorizer,
                'label_encoder': self.label_encoder,
                'feedback_data': self.feedback_data
            }
            
            with open(self.model_path, 'wb') as f:
                pickle.dump(model_data, f)
            logger.info("ML categorization model saved successfully")
        except Exception as e:
            logger.error(f"Error saving ML model: {e}")
    
    def _extract_features(self, contact: Dict[str, Any]) -> str:
        """Extract text features from contact for ML processing"""
        features = []
        
        # Combine all text fields
        name = contact.get('name', '').lower()
        email = contact.get('email', '').lower()
        phone = contact.get('phone', '').lower()
        address = contact.get('address', '').lower()
        notes = contact.get('notes', '').lower()
        
        # Create feature text
        feature_text = f"{name} {email} {phone} {address} {notes}"
        
        return feature_text.strip()
    
    def predict_category(self, contact: Dict[str, Any]) -> str:
        """Predict category using ML model or fallback to rule-based"""
        if self.model and self.vectorizer and self.label_encoder:
            try:
                feature_text = self._extract_features(contact)
                features = self.vectorizer.transform([feature_text])
                prediction = self.model.predict(features)[0]
                category = self.label_encoder.inverse_transform([prediction])[0]
                logger.debug(f"ML prediction for contact: {category}")
                return category
            except Exception as e:
                logger.warning(f"ML prediction failed: {e}, using rule-based fallback")
        
        # Fallback to rule-based categorization
        return self._rule_based_categorization(contact)
    
    def _rule_based_categorization(self, contact: Dict[str, Any]) -> str:
        """Enhanced rule-based categorization as fallback"""
        name = contact.get('name', '').lower()
        email = contact.get('email', '').lower()
        phone = contact.get('phone', '').lower()
        address = contact.get('address', '').lower()
        notes = contact.get('notes', '').lower()
        
        all_text = f"{name} {email} {phone} {address} {notes}".lower()
        
        # Work-related keywords (expanded)
        work_keywords = [
            'office', 'work', 'business', 'company', 'corp', 'corporation', 'enterprise',
            'ltd', 'limited', 'inc', 'incorporated', 'organization', 'org', 'department',
            'manager', 'director', 'ceo', 'cfo', 'hr', 'sales', 'marketing', 'finance',
            'legal', 'it', 'tech', 'professional', 'colleague', 'corporate', 'headquarters',
            'building', 'tower', 'complex', 'center', 'plaza', 'suite', 'floor',
            'project', 'team', 'meeting', 'conference', 'client', 'customer', 'vendor',
            'supplier', 'contractor', 'consultant', 'agency', 'firm', 'institute'
        ]
        
        # Personal keywords (expanded)
        personal_keywords = [
            'home', 'personal', 'friend', 'family', 'neighbor', 'buddy', 'mate',
            'college', 'school', 'university', 'gym', 'club', 'hobby', 'social',
            'residential', 'apartment', 'house', 'street', 'lane', 'avenue',
            'sister', 'brother', 'cousin', 'relative', 'gmail', 'yahoo', 'hotmail',
            'outlook', 'personal', 'private', 'individual'
        ]
        
        # Service keywords
        service_keywords = [
            'service', 'support', 'customer', 'help', 'assistance', 'provider',
            'repair', 'maintenance', 'delivery', 'transport', 'medical', 'doctor',
            'clinic', 'hospital', 'pharmacy', 'restaurant', 'shop', 'store'
        ]
        
        # Count keyword matches
        work_score = sum(1 for keyword in work_keywords if keyword in all_text)
        personal_score = sum(1 for keyword in personal_keywords if keyword in all_text)
        service_score = sum(1 for keyword in service_keywords if keyword in all_text)
        
        # Email domain analysis
        if email:
            domain = email.split('@')[-1] if '@' in email else ''
            if any(biz_domain in domain for biz_domain in ['company', 'corp', 'business', 'enterprise', 'org']):
                work_score += 2
            elif any(personal_domain in domain for personal_domain in ['gmail', 'yahoo', 'hotmail', 'outlook']):
                personal_score += 1
        
        # Determine category based on scores
        if work_score > personal_score and work_score > service_score:
            return "Work"
        elif personal_score > work_score and personal_score > service_score:
            return "Personal"
        elif service_score > 0:
            return "Service"
        else:
            return "Uncategorized"
    
    def add_feedback(self, contact: Dict[str, Any], correct_category: str):
        """Add user feedback for model improvement"""
        feature_text = self._extract_features(contact)
        self.feedback_data.append({
            'features': feature_text,
            'category': correct_category,
            'contact_id': contact.get('id')
        })
        
        logger.info(f"Added feedback: {correct_category} for contact {contact.get('id')}")
        
        # Retrain model if we have enough feedback data
        if len(self.feedback_data) >= 10:  # Minimum samples for training
            self._retrain_model()
    
    def _retrain_model(self):
        """Retrain the model with accumulated feedback"""
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.naive_bayes import MultinomialNB
            from sklearn.preprocessing import LabelEncoder
            from sklearn.pipeline import Pipeline
            
            if len(self.feedback_data) < 5:
                logger.warning("Not enough feedback data for retraining")
                return
            
            # Prepare training data
            texts = [item['features'] for item in self.feedback_data]
            labels = [item['category'] for item in self.feedback_data]
            
            # Create and train model
            self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
            self.label_encoder = LabelEncoder()
            self.model = MultinomialNB()
            
            # Transform data
            X = self.vectorizer.fit_transform(texts)
            y = self.label_encoder.fit_transform(labels)
            
            # Train model
            self.model.fit(X, y)
            
            # Save the updated model
            self._save_model()
            
            logger.info(f"Model retrained with {len(self.feedback_data)} feedback samples")
            
        except ImportError:
            logger.warning("scikit-learn not available, cannot retrain model")
        except Exception as e:
            logger.error(f"Error retraining model: {e}")

# Global categorizer instance
ml_categorizer = MLContactCategorizer()

def categorize_contact_ml(contact: Dict[str, Any]) -> str:
    """Main function for ML-based contact categorization"""
    return ml_categorizer.predict_category(contact)

def add_categorization_feedback(contact: Dict[str, Any], correct_category: str):
    """Add user feedback for improving categorization"""
    ml_categorizer.add_feedback(contact, correct_category)
