import React, { useState, useEffect } from 'react';
import { contactsApi } from '../utils/api';
import { validateContact } from '../utils/validation';

function AddContactModal({ contact, onClose }) {
  const [form, setForm] = useState({
    name: '',
    designation: '',
    company: '',
    telephone: '',
    email: '',
    website: '',
    category: 'Others',
    notes: '',
    // Legacy fields for backward compatibility
    phone: '',
    address: ''
  });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (contact) {
      setForm({
        name: contact.name || '',
        designation: contact.designation || '',
        company: contact.company || '',
        telephone: contact.telephone || contact.phone || '',
        email: contact.email || '',
        website: contact.website || '',
        category: contact.category || '',
        notes: contact.notes || '',
        // Legacy fields
        phone: contact.phone || '',
        address: contact.address || ''
      });
    }
  }, [contact]);

  const validateForm = () => {
    const validation = validateContact(form);
    setErrors(validation.errors);
    return validation.isValid;
  };

  const handleSubmit = async () => {
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setErrors({});

    try {
      if (contact) {
        await contactsApi.update(contact.id, form);
      } else {
        await contactsApi.create(form);
      }
      onClose();
    } catch (error) {
      if (error.response?.data?.detail) {
        setErrors({ general: error.response.data.detail });
      } else {
        setErrors({ general: 'Error saving contact: ' + error.message });
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white p-6 rounded shadow-xl w-full max-w-md max-h-[90vh] overflow-y-auto">
        <h2 className="text-lg font-bold mb-4">{contact ? 'Edit' : 'Add'} Contact</h2>

        {errors.general && (
          <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
            {errors.general}
          </div>
        )}

        <div className="space-y-4">
          <div>
            <input
              type="text"
              placeholder="Name *"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              className={`border p-2 w-full rounded ${errors.name ? 'border-red-500' : 'border-gray-300'}`}
              disabled={loading}
            />
            {errors.name && <p className="text-red-500 text-sm mt-1">{errors.name}</p>}
          </div>

          <div>
            <input
              type="text"
              placeholder="Designation"
              value={form.designation}
              onChange={(e) => setForm({ ...form, designation: e.target.value })}
              className="border border-gray-300 p-2 w-full rounded"
              disabled={loading}
            />
          </div>

          <div>
            <input
              type="text"
              placeholder="Company"
              value={form.company}
              onChange={(e) => setForm({ ...form, company: e.target.value })}
              className="border border-gray-300 p-2 w-full rounded"
              disabled={loading}
            />
          </div>

          <div>
            <input
              type="tel"
              placeholder="Telephone"
              value={form.telephone}
              onChange={(e) => setForm({ ...form, telephone: e.target.value })}
              className={`border p-2 w-full rounded ${errors.telephone ? 'border-red-500' : 'border-gray-300'}`}
              disabled={loading}
            />
            {errors.telephone && <p className="text-red-500 text-sm mt-1">{errors.telephone}</p>}
          </div>

          <div>
            <input
              type="email"
              placeholder="Email"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              className={`border p-2 w-full rounded ${errors.email ? 'border-red-500' : 'border-gray-300'}`}
              disabled={loading}
            />
            {errors.email && <p className="text-red-500 text-sm mt-1">{errors.email}</p>}
          </div>

          <div>
            <input
              type="url"
              placeholder="Website (e.g., https://example.com)"
              value={form.website}
              onChange={(e) => setForm({ ...form, website: e.target.value })}
              className="border border-gray-300 p-2 w-full rounded"
              disabled={loading}
            />
          </div>

          <div>
            <select
              value={form.category}
              onChange={(e) => setForm({ ...form, category: e.target.value })}
              className="border border-gray-300 p-2 w-full rounded"
              disabled={loading}
            >
              <option value="Others">Others</option>
              <optgroup label="Government & Diplomatic">
                <option value="Government">Government</option>
                <option value="Embassy">Embassy</option>
                <option value="Consulate">Consulate</option>
                <option value="High Commissioner">High Commissioner</option>
              </optgroup>
              <optgroup label="Business & Trade">
                <option value="Association">Association</option>
                <option value="Exporter">Exporter</option>
                <option value="Importer">Importer</option>
                <option value="Logistics">Logistics</option>
                <option value="Event Management">Event Management</option>
                <option value="Consultancy">Consultancy</option>
                <option value="Manufacturer">Manufacturer</option>
                <option value="Distributor">Distributor</option>
                <option value="Producer">Producer</option>
              </optgroup>
              <optgroup label="Professional Services">
                <option value="Healthcare">Healthcare</option>
                <option value="Education">Education</option>
                <option value="Finance">Finance</option>
              </optgroup>
              <optgroup label="General">
                <option value="Business">Business</option>
                <option value="Work">Work</option>
                <option value="Personal">Personal</option>
              </optgroup>
            </select>
          </div>

          <div>
            <textarea
              placeholder="Address"
              value={form.address}
              onChange={(e) => setForm({ ...form, address: e.target.value })}
              className="border border-gray-300 p-2 w-full rounded"
              rows="2"
              disabled={loading}
            />
          </div>

          <div>
            <textarea
              placeholder="Notes"
              value={form.notes}
              onChange={(e) => setForm({ ...form, notes: e.target.value })}
              className="border border-gray-300 p-2 w-full rounded"
              rows="3"
              disabled={loading}
            />
          </div>
        </div>

        <div className="flex justify-end gap-2 mt-6">
          <button
            onClick={onClose}
            className="text-gray-700 hover:underline"
            disabled={loading}
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={loading}
            className={`px-4 py-2 rounded ${
              loading
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700'
            } text-white`}
          >
            {loading ? 'Saving...' : 'Save'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default AddContactModal;