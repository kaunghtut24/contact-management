import { EMAIL_PATTERN, PHONE_PATTERN } from './constants';

export const validateEmail = (email) => {
  if (!email) return { isValid: true, error: null };
  
  if (!EMAIL_PATTERN.test(email)) {
    return { isValid: false, error: 'Please enter a valid email address' };
  }
  
  return { isValid: true, error: null };
};

export const validatePhone = (phone) => {
  if (!phone) return { isValid: true, error: null };
  
  if (!PHONE_PATTERN.test(phone)) {
    return { isValid: false, error: 'Please enter a valid phone number' };
  }
  
  return { isValid: true, error: null };
};

export const validateName = (name) => {
  if (!name || !name.trim()) {
    return { isValid: false, error: 'Name is required' };
  }
  
  if (name.trim().length < 2) {
    return { isValid: false, error: 'Name must be at least 2 characters long' };
  }
  
  return { isValid: true, error: null };
};

export const validateContact = (contact) => {
  const errors = {};
  
  const nameValidation = validateName(contact.name);
  if (!nameValidation.isValid) {
    errors.name = nameValidation.error;
  }
  
  const emailValidation = validateEmail(contact.email);
  if (!emailValidation.isValid) {
    errors.email = emailValidation.error;
  }
  
  const phoneValidation = validatePhone(contact.phone);
  if (!phoneValidation.isValid) {
    errors.phone = phoneValidation.error;
  }
  
  return {
    isValid: Object.keys(errors).length === 0,
    errors
  };
};
