// API Configuration
// Temporary override for testing - force Render backend URL
export const API_BASE_URL = 'https://contact-management-ffsl.onrender.com';
// export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Debug: Log the API URL being used
console.log('🔗 API_BASE_URL (Updated):', API_BASE_URL);
console.log('🔗 Environment variable VITE_API_BASE_URL:', import.meta.env.VITE_API_BASE_URL);
console.log('🔗 Cache buster timestamp:', new Date().toISOString());

// File Upload Configuration
export const SUPPORTED_FILE_TYPES = [
  'csv', 'xlsx', 'xls', 'pdf', 'docx', 'txt', 'vcf', 'vcard', 'jpg', 'jpeg', 'png'
];

export const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

// Contact Categories
export const CONTACT_CATEGORIES = [
  'Others',
  'Government',
  'Embassy',
  'Consulate',
  'High Commissioner',
  'Association',
  'Exporter',
  'Importer',
  'Logistics',
  'Event Management',
  'Consultancy',
  'Manufacturer',
  'Distributor',
  'Producer',
  'Healthcare',
  'Education',
  'Finance',
  'Business',
  'Work',
  'Personal'
];

// Validation Patterns
export const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
export const PHONE_PATTERN = /^[\d\s\-\+\(\)]+$/;

// UI Constants
export const ITEMS_PER_PAGE = 20;
export const DEBOUNCE_DELAY = 300; // milliseconds
