import React, { useState } from 'react';
import { contactsApi } from '../utils/api';
import { SUPPORTED_FILE_TYPES, MAX_FILE_SIZE } from '../utils/constants';

function UploadPage() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState('');

  const validateFile = (file) => {
    if (!file) {
      return { isValid: false, error: 'Please select a file' };
    }

    const fileExtension = file.name.split('.').pop().toLowerCase();
    if (!SUPPORTED_FILE_TYPES.includes(fileExtension)) {
      return {
        isValid: false,
        error: `File type not supported. Allowed types: ${SUPPORTED_FILE_TYPES.join(', ')}`
      };
    }

    if (file.size > MAX_FILE_SIZE) {
      return {
        isValid: false,
        error: `File size exceeds ${Math.round(MAX_FILE_SIZE / 1024 / 1024)}MB limit`
      };
    }

    return { isValid: true, error: null };
  };

  const handleUpload = async () => {
    const validation = validateFile(file);
    if (!validation.isValid) {
      setMessage(validation.error);
      return;
    }

    setUploading(true);

    // Show different messages based on file type
    const fileExtension = file.name.split('.').pop().toLowerCase();
    const isImageFile = ['jpg', 'jpeg', 'png', 'tiff', 'bmp'].includes(fileExtension);

    if (isImageFile) {
      setMessage('Processing image with OCR... This may take up to 60 seconds.');
    } else {
      setMessage('Uploading and processing file...');
    }

    try {
      const response = await contactsApi.upload(file);

      // Show detailed success message
      const data = response.data;
      let successMessage = `File uploaded successfully! `;

      if (data.contacts_created > 0) {
        successMessage += `${data.contacts_created} contacts created.`;
      }

      if (data.errors && data.errors.length > 0) {
        successMessage += ` ${data.errors.length} errors occurred.`;
      }

      if (data.ocr_used) {
        successMessage += ` (OCR processing completed)`;
      }

      setMessage(successMessage);
      setFile(null);
      // Reset file input
      document.querySelector('input[type="file"]').value = '';
    } catch (error) {
      let errorMessage = 'Error uploading file: ';

      if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
        errorMessage += 'Upload timed out. Please try with a smaller image or check your connection.';
      } else {
        errorMessage += (error.response?.data?.detail || error.message);
      }

      setMessage(errorMessage);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="p-4 max-w-md mx-auto">
      <h2 className="text-xl font-semibold mb-4">Upload Contacts</h2>
      <div className="mb-4">
        <input
          type="file"
          accept={SUPPORTED_FILE_TYPES.map(type => `.${type}`).join(',')}
          onChange={(e) => setFile(e.target.files[0])}
          className="border p-2 mb-2 w-full"
          disabled={uploading}
        />
        <p className="text-sm text-gray-600">
          Supported formats: {SUPPORTED_FILE_TYPES.join(', ').toUpperCase()}
        </p>
        <p className="text-sm text-gray-500">
          Maximum file size: {Math.round(MAX_FILE_SIZE / 1024 / 1024)}MB
        </p>
      </div>
      <button
        onClick={handleUpload}
        disabled={uploading || !file}
        className={`w-full p-2 rounded ${
          uploading || !file
            ? 'bg-gray-400 cursor-not-allowed'
            : 'bg-blue-500 hover:bg-blue-600'
        } text-white flex items-center justify-center`}
      >
        {uploading && (
          <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        )}
        {uploading ? 'Processing...' : 'Upload'}
      </button>
      {message && (
        <div className={`mt-4 p-2 rounded ${
          message.includes('Error')
            ? 'bg-red-100 text-red-700 border border-red-300'
            : 'bg-green-100 text-green-700 border border-green-300'
        }`}>
          {message}
        </div>
      )}
    </div>
  );
}

export default UploadPage;