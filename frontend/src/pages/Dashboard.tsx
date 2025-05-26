import React, { useState } from 'react';

const Dashboard = () => {
  return (
    <div className="space-y-6">
      {/* Document area */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-medium text-gray-900">Recent Documents</h2>
          <div className="flex space-x-2">
            <button className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary">
              Upload
            </button>
            <button className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary">
              New Folder
            </button>
          </div>
        </div>
        
        <div className="border-t border-gray-200 pt-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* Document card */}
            <div className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex items-center">
                  <svg className="h-8 w-8 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clipRule="evenodd" />
                  </svg>
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-gray-900">Contract.pdf</h3>
                    <p className="text-xs text-gray-500">PDF • 2.4 MB</p>
                  </div>
                </div>
                <button className="text-gray-400 hover:text-gray-500">
                  <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
                  </svg>
                </button>
              </div>
              <div className="mt-2 text-xs text-gray-500">
                <p>Last modified: May 24, 2025</p>
              </div>
            </div>
            
            {/* Document card */}
            <div className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex items-center">
                  <svg className="h-8 w-8 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clipRule="evenodd" />
                  </svg>
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-gray-900">Client_Form.pdf</h3>
                    <p className="text-xs text-gray-500">PDF • 1.2 MB</p>
                  </div>
                </div>
                <button className="text-gray-400 hover:text-gray-500">
                  <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
                  </svg>
                </button>
              </div>
              <div className="mt-2 text-xs text-gray-500">
                <p>Last modified: May 23, 2025</p>
              </div>
            </div>
            
            {/* Document card */}
            <div className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex items-center">
                  <svg className="h-8 w-8 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clipRule="evenodd" />
                  </svg>
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-gray-900">Meeting_Notes.docx</h3>
                    <p className="text-xs text-gray-500">DOCX • 0.8 MB</p>
                  </div>
                </div>
                <button className="text-gray-400 hover:text-gray-500">
                  <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
                  </svg>
                </button>
              </div>
              <div className="mt-2 text-xs text-gray-500">
                <p>Last modified: May 22, 2025</p>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Chat area */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-xl font-medium text-gray-900 mb-6">AI Assistant Chat</h2>
        
        <div className="border border-gray-200 rounded-lg h-96 flex flex-col">
          <div className="flex-1 p-4 overflow-y-auto space-y-4">
            {/* AI message */}
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <div className="h-10 w-10 rounded-full bg-primary flex items-center justify-center text-white">
                  AI
                </div>
              </div>
              <div className="ml-3 bg-gray-100 rounded-lg py-2 px-4 max-w-3xl">
                <p className="text-sm text-gray-900">Hello! I'm your Watkibot Law Assistant. How can I help you today? I can help you fill out forms, organize documents, or answer questions about your cases.</p>
              </div>
            </div>
            
            {/* User message */}
            <div className="flex items-start justify-end">
              <div className="bg-primary rounded-lg py-2 px-4 max-w-3xl">
                <p className="text-sm text-white">I need help filling out the client intake form for the Smith case.</p>
              </div>
              <div className="ml-3 flex-shrink-0">
                <div className="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center text-gray-700">
                  You
                </div>
              </div>
            </div>
            
            {/* AI message */}
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <div className="h-10 w-10 rounded-full bg-primary flex items-center justify-center text-white">
                  AI
                </div>
              </div>
              <div className="ml-3 bg-gray-100 rounded-lg py-2 px-4 max-w-3xl">
                <p className="text-sm text-gray-900">I'd be happy to help you fill out the client intake form. I'll analyze the documents in the Smith case folder to extract the relevant information. Would you like me to open the form now and start filling it out?</p>
              </div>
            </div>
          </div>
          
          <div className="border-t border-gray-200 p-4">
            <div className="flex space-x-3">
              <input
                type="text"
                className="flex-1 focus:ring-primary focus:border-primary block w-full min-w-0 rounded-md sm:text-sm border-gray-300"
                placeholder="Type your message..."
              />
              <button className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary">
                Send
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
