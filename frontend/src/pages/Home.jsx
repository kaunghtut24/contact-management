import React from 'react';
import UploadPage from '../components/UploadPage';
import ContactsList from '../components/ContactsList';

function Home() {
  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-blue-600 text-white p-4">
        <h1 className="text-2xl font-bold">Contact Management System</h1>
      </header>
      <main className="p-4">
        <UploadPage />
        <ContactsList />
      </main>
    </div>
  );
}

export default Home;