import React, { useState } from 'react';

const Documents = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [currentFolder, setCurrentFolder] = useState('root');
  
  // Mock data for folders and documents
  const folders = [
    { id: 'folder1', name: 'Client Documents', parentId: 'root' },
    { id: 'folder2', name: 'Court Filings', parentId: 'root' },
    { id: 'folder3', name: 'Evidence', parentId: 'root' },
    { id: 'folder4', name: 'Contracts', parentId: 'folder1' },
  ];
  
  const documents = [
    { id: 'doc1', name: 'Contract.pdf', type: 'pdf', size: '2.4 MB', modified: 'May 24, 2025', folderId: 'root' },
    { id: 'doc2', name: 'Client_Form.pdf', type: 'pdf', size: '1.2 MB', modified: 'May 23, 2025', folderId: 'root' },
    { id: 'doc3', name: 'Meeting_Notes.docx', type: 'docx', size: '0.8 MB', modified: 'May 22, 2025', folderId: 'root' },
    { id: 'doc4', name: 'Deposition.pdf', type: 'pdf', size: '3.1 MB', modified: 'May 21, 2025', folderId: 'folder2' },
    { id: 'doc5', name: 'Evidence_Photo.jpg', type: 'jpg', size: '1.5 MB', modified: 'May 20, 2025', folderId: 'folder3' },
  ];
  
  // Filter folders and documents based on current folder and search term
  const currentFolders = folders.filter(folder => 
    folder.parentId === currentFolder && 
    folder.name.toLowerCase().includes(searchTerm.toLowerCase())
  );
  
  const currentDocuments = documents.filter(doc => 
    doc.folderId === currentFolder && 
    doc.name.toLowerCase().includes(searchTerm.toLowerCase())
  );
  
  // Handle folder navigation
  const navigateToFolder = (folderId: string) => {
    setCurrentFolder(folderId);
  };
  
  // Handle navigation to parent folder
  const navigateToParent = () => {
    const currentFolderObj = folders.find(f => f.id === currentFolder);
    if (currentFolderObj) {
      setCurrentFolder(currentFolderObj.parentId);
    }
  };
  
  // Get current folder name
  const getCurrentFolderName = () => {
    if (currentFolder === 'root') return 'All Documents';
    const folder = folders.find(f => f.id === currentFolder);
    return folder ? folder.name : 'Unknown Folder';
  };
  
  return (
    <div className="bg-white shadow rounded-lg p-6">
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center">
          <h2 className="text-xl font-medium text-gray-900">{getCurrentFolderName()}</h2>
          {currentFolder !== 'root' && (
            <button 
              onClick={navigateToParent}
              className="ml-2 text-sm text-primary hover:text-primary-dark"
            >
              (Back to parent)
            </button>
          )}
        </div>
        <div className="flex space-x-2">
          <div className="relative">
            <input
              type="text"
              className="focus:ring-primary focus:border-primary block w-full pr-10 sm:text-sm border-gray-300 rounded-md"
              placeholder="Search documents..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
              <svg className="h-5 w-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clipRule="evenodd" />
              </svg>
            </div>
          </div>
          <button className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary">
            Upload
          </button>
          <button className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary">
            New Folder
          </button>
        </div>
      </div>
      
      <div className="border-t border-gray-200 pt-4">
        {/* Folders */}
        {currentFolders.length > 0 && (
          <div className="mb-6">
            <h3 className="text-sm font-medium text-gray-500 mb-3">Folders</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {currentFolders.map((folder) => (
                <div 
                  key={folder.id}
                  onClick={() => navigateToFolder(folder.id)}
                  className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
                >
                  <div className="flex items-center">
                    <svg className="h-8 w-8 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M2 6a2 2 0 012-2h5l2 2h5a2 2 0 012 2v6a2 2 0 01-2 2H4a2 2 0 01-2-2V6z" clipRule="evenodd" />
                    </svg>
                    <div className="ml-3">
                      <h3 className="text-sm font-medium text-gray-900">{folder.name}</h3>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
        
        {/* Documents */}
        <div>
          <h3 className="text-sm font-medium text-gray-500 mb-3">Documents</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {currentDocuments.map((doc) => (
              <div key={doc.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between">
                  <div className="flex items-center">
                    <svg className="h-8 w-8 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clipRule="evenodd" />
                    </svg>
                    <div className="ml-3">
                      <h3 className="text-sm font-medium text-gray-900">{doc.name}</h3>
                      <p className="text-xs text-gray-500">{doc.type.toUpperCase()} • {doc.size}</p>
                    </div>
                  </div>
                  <button className="text-gray-400 hover:text-gray-500">
                    <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
                    </svg>
                  </button>
                </div>
                <div className="mt-2 text-xs text-gray-500">
                  <p>Last modified: {doc.modified}</p>
                </div>
              </div>
            ))}
            
            {currentDocuments.length === 0 && (
              <div className="col-span-3 text-center py-12 text-gray-500">
                No documents found in this folder.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Documents;
