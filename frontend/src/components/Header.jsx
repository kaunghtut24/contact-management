import React from 'react';
import { useAuth } from '../contexts/AuthContext';

function Header() {
  const { user, logout, isAdmin } = useAuth();

  const handleLogout = () => {
    if (window.confirm('Are you sure you want to logout?')) {
      logout();
    }
  };

  return (
    <header className="bg-blue-600 text-white p-4 shadow-lg">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Contact Management System</h1>
          <p className="text-blue-100 text-sm">Secure contact management with authentication</p>
        </div>
        
        <div className="flex items-center space-x-4">
          <div className="text-right">
            <p className="text-sm font-medium">Welcome, {user?.full_name || user?.username}</p>
            <p className="text-xs text-blue-200">
              {isAdmin() ? '👑 Administrator' : '👤 User'} • {user?.email}
            </p>
          </div>
          
          <button
            onClick={handleLogout}
            className="bg-blue-700 hover:bg-blue-800 px-4 py-2 rounded-md text-sm font-medium transition-colors duration-200"
          >
            Logout
          </button>
        </div>
      </div>
    </header>
  );
}

export default Header;
