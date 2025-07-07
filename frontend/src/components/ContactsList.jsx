import React, { useEffect, useState } from 'react';
import { contactsApi } from '../utils/api';
import { CONTACT_CATEGORIES } from '../utils/constants';
import AddContactModal from './AddContactModal';

function ContactsList() {
  const [contacts, setContacts] = useState([]);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingContact, setEditingContact] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [selectedContacts, setSelectedContacts] = useState(new Set());
  const [selectAll, setSelectAll] = useState(false);

  const getCategoryColor = (category) => {
    const colors = {
      'Government': 'bg-blue-100 text-blue-800',
      'Embassy': 'bg-purple-100 text-purple-800',
      'Consulate': 'bg-indigo-100 text-indigo-800',
      'High Commissioner': 'bg-violet-100 text-violet-800',
      'Association': 'bg-green-100 text-green-800',
      'Exporter': 'bg-orange-100 text-orange-800',
      'Importer': 'bg-yellow-100 text-yellow-800',
      'Logistics': 'bg-teal-100 text-teal-800',
      'Event Management': 'bg-pink-100 text-pink-800',
      'Consultancy': 'bg-lime-100 text-lime-800',
      'Manufacturer': 'bg-amber-100 text-amber-800',
      'Distributor': 'bg-sky-100 text-sky-800',
      'Producer': 'bg-rose-100 text-rose-800',
      'Healthcare': 'bg-red-100 text-red-800',
      'Education': 'bg-cyan-100 text-cyan-800',
      'Finance': 'bg-emerald-100 text-emerald-800',
      'Work': 'bg-blue-100 text-blue-800',
      'Personal': 'bg-green-100 text-green-800',
      'Business': 'bg-gray-100 text-gray-800',
      'Others': 'bg-gray-100 text-gray-600'
    };
    return colors[category] || 'bg-gray-100 text-gray-600';
  };

  useEffect(() => {
    fetchContacts();
  }, [search, category]);

  const fetchContacts = async () => {
    setLoading(true);
    setError('');
    try {
      const params = {};
      if (search) params.search = search;
      if (category) params.category = category;
      const res = await contactsApi.getAll(params);
      setContacts(res.data);
    } catch (error) {
      console.error('Error fetching contacts:', error);
      setError('Failed to fetch contacts. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this contact?')) {
      try {
        await contactsApi.delete(id);
        fetchContacts();
      } catch (error) {
        alert('Error deleting contact: ' + error.message);
      }
    }
  };

  const handleExport = () => {
    window.location.href = 'http://localhost:8000/export';
  };

  // Selection handling functions
  const handleSelectAll = (checked) => {
    setSelectAll(checked);
    if (checked) {
      setSelectedContacts(new Set(contacts.map(contact => contact.id)));
    } else {
      setSelectedContacts(new Set());
    }
  };

  const handleSelectContact = (contactId, checked) => {
    const newSelected = new Set(selectedContacts);
    if (checked) {
      newSelected.add(contactId);
    } else {
      newSelected.delete(contactId);
    }
    setSelectedContacts(newSelected);
    setSelectAll(newSelected.size === contacts.length && contacts.length > 0);
  };

  // Batch operations
  const handleBatchDelete = async () => {
    if (selectedContacts.size === 0) {
      alert('Please select contacts to delete');
      return;
    }

    if (window.confirm(`Are you sure you want to delete ${selectedContacts.size} selected contacts?`)) {
      try {
        const response = await fetch('http://localhost:8000/contacts/batch', {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(Array.from(selectedContacts)),
        });

        if (response.ok) {
          const result = await response.json();
          alert(`Successfully deleted ${result.deleted_count} contacts`);
          setSelectedContacts(new Set());
          setSelectAll(false);
          fetchContacts();
        } else {
          alert('Error deleting contacts');
        }
      } catch (error) {
        alert('Error deleting contacts: ' + error.message);
      }
    }
  };

  const handleBatchExport = async () => {
    if (selectedContacts.size === 0) {
      alert('Please select contacts to export');
      return;
    }

    try {
      const response = await fetch('http://localhost:8000/export/batch', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(Array.from(selectedContacts)),
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `selected_contacts_${selectedContacts.size}.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
      } else {
        alert('Error exporting contacts');
      }
    } catch (error) {
      alert('Error exporting contacts: ' + error.message);
    }
  };

  return (
    <div className="p-4">
      <h2 className="text-xl font-semibold mb-4">Contacts</h2>
      <div className="mb-4 flex flex-col sm:flex-row gap-2">
        <input
          type="text"
          placeholder="Search"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="border p-2 flex-1"
        />
        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          className="border p-2"
        >
          <option value="">All Categories</option>
          {CONTACT_CATEGORIES.map(category => (
            <option key={category} value={category}>{category}</option>
          ))}
        </select>
        <button
          onClick={() => setShowModal(true)}
          className="bg-blue-500 text-white p-2 rounded hover:bg-blue-600"
        >
          Add Contact
        </button>
        <button
          onClick={handleExport}
          className="bg-green-500 text-white p-2 rounded hover:bg-green-600"
        >
          Export All
        </button>

        {/* Batch operation buttons */}
        {selectedContacts.size > 0 && (
          <>
            <button
              onClick={handleBatchExport}
              className="bg-blue-500 text-white p-2 rounded hover:bg-blue-600"
            >
              Export Selected ({selectedContacts.size})
            </button>
            <button
              onClick={handleBatchDelete}
              className="bg-red-500 text-white p-2 rounded hover:bg-red-600"
            >
              Delete Selected ({selectedContacts.size})
            </button>
          </>
        )}
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      {loading && (
        <div className="text-center py-4">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          <p className="mt-2 text-gray-600">Loading contacts...</p>
        </div>
      )}
      {!loading && (
        <div className="overflow-x-auto">
          <table className="w-full table-auto border-collapse border border-gray-300 min-w-max">
            <thead>
              <tr className="bg-gray-100">
                <th className="border p-2 text-left sticky left-0 bg-gray-100 z-10 min-w-[100px]">
                  <input
                    type="checkbox"
                    checked={selectAll}
                    onChange={(e) => handleSelectAll(e.target.checked)}
                    className="mr-2"
                  />
                  Select
                </th>
                <th className="border p-2 text-left min-w-[150px]">Name</th>
                <th className="border p-2 text-left min-w-[120px]">Designation</th>
                <th className="border p-2 text-left min-w-[150px]">Company</th>
                <th className="border p-2 text-left min-w-[120px]">Telephone</th>
                <th className="border p-2 text-left min-w-[200px]">Email</th>
                <th className="border p-2 text-left min-w-[150px]">Website</th>
                <th className="border p-2 text-left min-w-[100px]">Category</th>
                <th className="border p-2 text-left min-w-[200px]">Address</th>
                <th className="border p-2 text-left min-w-[200px]">Notes</th>
                <th className="border p-2 text-left min-w-[120px] sticky right-0 bg-gray-100 z-10">Actions</th>
              </tr>
            </thead>
            <tbody>
              {contacts.map(contact => (
                <tr key={contact.id} className="border-t hover:bg-gray-50">
                  <td className="border p-2 sticky left-0 bg-white z-5">
                    <input
                      type="checkbox"
                      checked={selectedContacts.has(contact.id)}
                      onChange={(e) => handleSelectContact(contact.id, e.target.checked)}
                      className="mr-2"
                    />
                  </td>
                  <td className="border p-2 font-medium">{contact.name}</td>
                  <td className="border p-2">{contact.designation || '-'}</td>
                  <td className="border p-2">{contact.company || '-'}</td>
                  <td className="border p-2">{contact.telephone || contact.phone || '-'}</td>
                  <td className="border p-2">
                    {contact.email ? (
                      <a href={`mailto:${contact.email}`} className="text-blue-600 hover:underline">
                        {contact.email}
                      </a>
                    ) : '-'}
                  </td>
                  <td className="border p-2">
                    {contact.website ? (
                      <a href={contact.website} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                        {contact.website.replace(/^https?:\/\//, '')}
                      </a>
                    ) : '-'}
                  </td>
                  <td className="border p-2">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${getCategoryColor(contact.category)}`}>
                      {contact.category}
                    </span>
                  </td>
                  <td className="border p-2">
                    <div className="text-sm text-gray-600 max-w-[200px] truncate" title={contact.address || ''}>
                      {contact.address || '-'}
                    </div>
                  </td>
                  <td className="border p-2">
                    <div className="text-sm text-gray-600 max-w-[200px] truncate" title={contact.notes || ''}>
                      {contact.notes || '-'}
                    </div>
                  </td>
                  <td className="border p-2 sticky right-0 bg-white z-5">
                    <div className="flex gap-2">
                      <button
                        onClick={() => { setEditingContact(contact); setShowModal(true); }}
                        className="text-blue-500 hover:underline text-sm"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDelete(contact.id)}
                        className="text-red-500 hover:underline text-sm"
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showModal && (
        <AddContactModal
          contact={editingContact}
          onClose={() => {
            setShowModal(false);
            setEditingContact(null);
            fetchContacts();
          }}
        />
      )}
    </div>
  );
}

export default ContactsList;