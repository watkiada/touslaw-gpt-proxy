import React, { useState } from 'react';

const Settings = () => {
  const [settings, setSettings] = useState({
    openaiApiKey: 'sk-••••••••••••••••••••••••••••••••••••••••••••',
    pineconeApiKey: 'a1b2c3d4-••••-••••-••••-••••••••••••',
    aiModel: 'gpt-4',
    maxTokens: 4000,
    temperature: 0.7,
    enableAutoFiling: true,
    enableOcr: true,
    defaultCaseId: 1,
    defaultOfficeId: 1
  });
  
  const [isSaving, setIsSaving] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [showApiKey, setShowApiKey] = useState(false);
  const [showPineconeKey, setShowPineconeKey] = useState(false);
  
  // Handle input changes
  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setSettings({
      ...settings,
      [name]: value
    });
  };
  
  // Handle checkbox changes
  const handleCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, checked } = e.target;
    setSettings({
      ...settings,
      [name]: checked
    });
  };
  
  // Handle form submission
  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsSaving(true);
    
    // Simulate API call
    setTimeout(() => {
      setIsSaving(false);
      setShowSuccess(true);
      
      // Hide success message after 3 seconds
      setTimeout(() => {
        setShowSuccess(false);
      }, 3000);
    }, 1500);
  };
  
  return (
    <div className="bg-white shadow rounded-lg p-6">
      <h2 className="text-xl font-medium text-gray-900 mb-6">AI Configuration Settings</h2>
      
      {showSuccess && (
        <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-md">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-green-800">
                Settings saved successfully!
              </p>
            </div>
          </div>
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-4">API Keys</h3>
          <div className="space-y-4">
            <div>
              <label htmlFor="openaiApiKey" className="block text-sm font-medium text-gray-700">OpenAI API Key</label>
              <div className="mt-1 relative rounded-md shadow-sm">
                <input
                  type={showApiKey ? "text" : "password"}
                  name="openaiApiKey"
                  id="openaiApiKey"
                  value={settings.openaiApiKey}
                  onChange={handleInputChange}
                  className="focus:ring-primary focus:border-primary block w-full pr-10 sm:text-sm border-gray-300 rounded-md"
                />
                <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
                  <button
                    type="button"
                    onClick={() => setShowApiKey(!showApiKey)}
                    className="text-gray-400 hover:text-gray-500 focus:outline-none"
                  >
                    {showApiKey ? (
                      <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                        <path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd" />
                      </svg>
                    ) : (
                      <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M3.707 2.293a1 1 0 00-1.414 1.414l14 14a1 1 0 001.414-1.414l-1.473-1.473A10.014 10.014 0 0019.542 10C18.268 5.943 14.478 3 10 3a9.958 9.958 0 00-4.512 1.074l-1.78-1.781zm4.261 4.26l1.514 1.515a2.003 2.003 0 012.45 2.45l1.514 1.514a4 4 0 00-5.478-5.478z" clipRule="evenodd" />
                        <path d="M12.454 16.697L9.75 13.992a4 4 0 01-3.742-3.741L2.335 6.578A9.98 9.98 0 00.458 10c1.274 4.057 5.065 7 9.542 7 .847 0 1.669-.105 2.454-.303z" />
                      </svg>
                    )}
                  </button>
                </div>
              </div>
              <p className="mt-1 text-sm text-gray-500">Your OpenAI API key is required for AI functionality.</p>
            </div>
            
            <div>
              <label htmlFor="pineconeApiKey" className="block text-sm font-medium text-gray-700">Pinecone API Key</label>
              <div className="mt-1 relative rounded-md shadow-sm">
                <input
                  type={showPineconeKey ? "text" : "password"}
                  name="pineconeApiKey"
                  id="pineconeApiKey"
                  value={settings.pineconeApiKey}
                  onChange={handleInputChange}
                  className="focus:ring-primary focus:border-primary block w-full pr-10 sm:text-sm border-gray-300 rounded-md"
                />
                <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
                  <button
                    type="button"
                    onClick={() => setShowPineconeKey(!showPineconeKey)}
                    className="text-gray-400 hover:text-gray-500 focus:outline-none"
                  >
                    {showPineconeKey ? (
                      <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                        <path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd" />
                      </svg>
                    ) : (
                      <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M3.707 2.293a1 1 0 00-1.414 1.414l14 14a1 1 0 001.414-1.414l-1.473-1.473A10.014 10.014 0 0019.542 10C18.268 5.943 14.478 3 10 3a9.958 9.958 0 00-4.512 1.074l-1.78-1.781zm4.261 4.26l1.514 1.515a2.003 2.003 0 012.45 2.45l1.514 1.514a4 4 0 00-5.478-5.478z" clipRule="evenodd" />
                        <path d="M12.454 16.697L9.75 13.992a4 4 0 01-3.742-3.741L2.335 6.578A9.98 9.98 0 00.458 10c1.274 4.057 5.065 7 9.542 7 .847 0 1.669-.105 2.454-.303z" />
                      </svg>
                    )}
                  </button>
                </div>
              </div>
              <p className="mt-1 text-sm text-gray-500">Required for vector search and document embedding.</p>
            </div>
          </div>
        </div>
        
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-4">AI Model Settings</h3>
          <div className="space-y-4">
            <div>
              <label htmlFor="aiModel" className="block text-sm font-medium text-gray-700">AI Model</label>
              <select
                id="aiModel"
                name="aiModel"
                value={settings.aiModel}
                onChange={handleInputChange}
                className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary focus:border-primary sm:text-sm rounded-md"
              >
                <option value="gpt-4">GPT-4 (Recommended)</option>
                <option value="gpt-4-turbo">GPT-4 Turbo</option>
                <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
              </select>
              <p className="mt-1 text-sm text-gray-500">Select the AI model to use for document analysis and chat.</p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="maxTokens" className="block text-sm font-medium text-gray-700">Max Tokens</label>
                <input
                  type="number"
                  name="maxTokens"
                  id="maxTokens"
                  min="1"
                  max="8000"
                  value={settings.maxTokens}
                  onChange={handleInputChange}
                  className="mt-1 focus:ring-primary focus:border-primary block w-full sm:text-sm border-gray-300 rounded-md"
                />
                <p className="mt-1 text-sm text-gray-500">Maximum tokens per API request.</p>
              </div>
              
              <div>
                <label htmlFor="temperature" className="block text-sm font-medium text-gray-700">Temperature</label>
                <input
                  type="range"
                  name="temperature"
                  id="temperature"
                  min="0"
                  max="1"
                  step="0.1"
                  value={settings.temperature}
                  onChange={handleInputChange}
                  className="mt-1 w-full"
                />
                <div className="flex justify-between text-xs text-gray-500">
                  <span>Precise (0.0)</span>
                  <span>Balanced ({settings.temperature})</span>
                  <span>Creative (1.0)</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-4">Feature Settings</h3>
          <div className="space-y-4">
            <div className="flex items-start">
              <div className="flex items-center h-5">
                <input
                  id="enableAutoFiling"
                  name="enableAutoFiling"
                  type="checkbox"
                  checked={settings.enableAutoFiling}
                  onChange={handleCheckboxChange}
                  className="focus:ring-primary h-4 w-4 text-primary border-gray-300 rounded"
                />
              </div>
              <div className="ml-3 text-sm">
                <label htmlFor="enableAutoFiling" className="font-medium text-gray-700">Enable Auto-Filing</label>
                <p className="text-gray-500">Automatically organize and file documents based on content analysis.</p>
              </div>
            </div>
            
            <div className="flex items-start">
              <div className="flex items-center h-5">
                <input
                  id="enableOcr"
                  name="enableOcr"
                  type="checkbox"
                  checked={settings.enableOcr}
                  onChange={handleCheckboxChange}
                  className="focus:ring-primary h-4 w-4 text-primary border-gray-300 rounded"
                />
              </div>
              <div className="ml-3 text-sm">
                <label htmlFor="enableOcr" className="font-medium text-gray-700">Enable OCR Processing</label>
                <p className="text-gray-500">Extract text from scanned documents and images.</p>
              </div>
            </div>
          </div>
        </div>
        
        <div className="flex justify-end space-x-3">
          <button
            type="button"
            className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
          >
            Reset to Defaults
          </button>
          <button
            type="submit"
            disabled={isSaving}
            className={`px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white ${isSaving ? 'bg-gray-400' : 'bg-primary hover:bg-primary-dark'} focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary`}
          >
            {isSaving ? 'Saving...' : 'Save Settings'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default Settings;
