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
    setMessage('');

    try {
      await contactsApi.upload(file);
      setMessage('File uploaded successfully');
      setFile(null);
      // Reset file input
      document.querySelector('input[type="file"]').value = '';
    } catch (error) {
      let errorMessage = 'Error uploading file: ';

      if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
        errorMessage += 'Upload timed out. Please try with a smaller image or check your connection.';
      } else if (error.response?.data?.timeout) {
        errorMessage += 'Processing timed out. Please try with a smaller or clearer image.';
      } else if (error.response?.status === 401) {
        errorMessage += 'Authentication expired. Please refresh the page and login again.';
      } else {
        const detail = error.response?.data?.detail || error.message;
        if (detail.includes('timed out')) {
          errorMessage += 'Processing timed out. Please try with a smaller image.';
        } else {
          errorMessage += detail;
        }
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
        } text-white`}
      >
        {uploading ? 'Uploading...' : 'Upload'}
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