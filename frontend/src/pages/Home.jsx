import React from 'react';
import Header from '../components/Header';
import UploadPage from '../components/UploadPage';
import ContactsList from '../components/ContactsList';

function Home() {
  return (
    <div className="min-h-screen bg-gray-100">
      <Header />
      <main className="p-4">
        <UploadPage />
        <ContactsList />
      </main>
    </div>
  );
}

export default Home;