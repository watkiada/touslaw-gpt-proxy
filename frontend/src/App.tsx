import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';

// Components for different pages
const Dashboard = React.lazy(() => import('./pages/Dashboard'));
const Documents = React.lazy(() => import('./pages/Documents'));
const PDFFormViewer = React.lazy(() => import('./pages/PDFFormViewer'));
const Chat = React.lazy(() => import('./pages/Chat'));
const Settings = React.lazy(() => import('./pages/Settings'));
const LetterheadSettings = React.lazy(() => import('./pages/LetterheadSettings'));

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <header className="bg-white shadow">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-6">
              <div className="flex items-center">
                <h1 className="text-3xl font-bold text-primary">Watkibot Law Assistant</h1>
              </div>
              <div className="flex items-center space-x-4">
                <Link to="/settings" className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary">
                  Settings
                </Link>
                <button className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-secondary hover:bg-secondary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-secondary">
                  Logout
                </button>
              </div>
            </div>
          </div>
        </header>

        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            {/* Sidebar */}
            <div className="lg:col-span-1 bg-white shadow rounded-lg p-4">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Cases</h2>
              <nav className="space-y-2">
                <Link to="/cases/smith-vs-johnson" className="block px-3 py-2 rounded-md text-sm font-medium text-white bg-primary hover:bg-primary-dark">
                  Smith vs. Johnson
                </Link>
                <Link to="/cases/doe-inheritance" className="block px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-100">
                  Doe Inheritance
                </Link>
                <Link to="/cases/corporate-merger" className="block px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-100">
                  Corporate Merger
                </Link>
              </nav>
              
              <h2 className="text-lg font-medium text-gray-900 mt-6 mb-4">Documents</h2>
              <nav className="space-y-2">
                <Link to="/documents" className="block px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-100">
                  All Documents
                </Link>
                <Link to="/documents/recent" className="block px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-100">
                  Recent
                </Link>
                <Link to="/documents/forms" className="block px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-100">
                  Forms
                </Link>
              </nav>
              
              <h2 className="text-lg font-medium text-gray-900 mt-6 mb-4">Settings</h2>
              <nav className="space-y-2">
                <Link to="/settings/office" className="block px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-100">
                  Office Profile
                </Link>
                <Link to="/settings/letterhead" className="block px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-100">
                  Letterhead
                </Link>
                <Link to="/settings/ai" className="block px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-100">
                  AI Configuration
                </Link>
              </nav>
            </div>

            {/* Main content */}
            <div className="lg:col-span-3 space-y-6">
              <React.Suspense fallback={<div className="text-center py-12">Loading...</div>}>
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/documents/*" element={<Documents />} />
                  <Route path="/documents/forms/:formId" element={<PDFFormViewer />} />
                  <Route path="/chat" element={<Chat />} />
                  <Route path="/settings" element={<Settings />} />
                  <Route path="/settings/letterhead" element={<LetterheadSettings />} />
                  {/* Add more routes as needed */}
                </Routes>
              </React.Suspense>
            </div>
          </div>
        </main>
      </div>
    </Router>
  );
}

export default App;
