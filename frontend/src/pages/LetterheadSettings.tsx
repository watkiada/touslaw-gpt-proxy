import React, { useState } from 'react';

interface Letterhead {
  firmName: string;
  address: string;
  city: string;
  state: string;
  zipCode: string;
  phone: string;
  email: string;
  website: string;
  logo: File | null;
}

const LetterheadSettings = () => {
  const [letterhead, setLetterhead] = useState<Letterhead>({
    firmName: 'Smith & Associates Law Firm',
    address: '123 Legal Avenue, Suite 500',
    city: 'New York',
    state: 'NY',
    zipCode: '10001',
    phone: '(212) 555-1234',
    email: 'contact@smithlaw.com',
    website: 'www.smithlaw.com',
    logo: null
  });
  
  const [logoPreview, setLogoPreview] = useState<string | ArrayBuffer | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  
  // Handle input changes
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setLetterhead({
      ...letterhead,
      [name]: value
    });
  };
  
  // Handle logo upload
  const handleLogoUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setLogoPreview(reader.result as string);
        setLetterhead({
          ...letterhead,
          logo: file
        });
      };
      reader.readAsDataURL(file);
    }
  };
  
  // Handle form submission
  const handleSubmit = (e: React.FormEvent) => {
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
      <h2 className="text-xl font-medium text-gray-900 mb-6">Letterhead Settings</h2>
      
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
                Letterhead settings saved successfully!
              </p>
            </div>
          </div>
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label htmlFor="firmName" className="block text-sm font-medium text-gray-700">Firm Name</label>
            <input
              type="text"
              name="firmName"
              id="firmName"
              value={letterhead.firmName}
              onChange={handleInputChange}
              className="mt-1 focus:ring-primary focus:border-primary block w-full sm:text-sm border-gray-300 rounded-md"
            />
          </div>
          
          <div>
            <label htmlFor="address" className="block text-sm font-medium text-gray-700">Address</label>
            <input
              type="text"
              name="address"
              id="address"
              value={letterhead.address}
              onChange={handleInputChange}
              className="mt-1 focus:ring-primary focus:border-primary block w-full sm:text-sm border-gray-300 rounded-md"
            />
          </div>
          
          <div>
            <label htmlFor="city" className="block text-sm font-medium text-gray-700">City</label>
            <input
              type="text"
              name="city"
              id="city"
              value={letterhead.city}
              onChange={handleInputChange}
              className="mt-1 focus:ring-primary focus:border-primary block w-full sm:text-sm border-gray-300 rounded-md"
            />
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="state" className="block text-sm font-medium text-gray-700">State</label>
              <input
                type="text"
                name="state"
                id="state"
                value={letterhead.state}
                onChange={handleInputChange}
                className="mt-1 focus:ring-primary focus:border-primary block w-full sm:text-sm border-gray-300 rounded-md"
              />
            </div>
            <div>
              <label htmlFor="zipCode" className="block text-sm font-medium text-gray-700">Zip Code</label>
              <input
                type="text"
                name="zipCode"
                id="zipCode"
                value={letterhead.zipCode}
                onChange={handleInputChange}
                className="mt-1 focus:ring-primary focus:border-primary block w-full sm:text-sm border-gray-300 rounded-md"
              />
            </div>
          </div>
          
          <div>
            <label htmlFor="phone" className="block text-sm font-medium text-gray-700">Phone</label>
            <input
              type="text"
              name="phone"
              id="phone"
              value={letterhead.phone}
              onChange={handleInputChange}
              className="mt-1 focus:ring-primary focus:border-primary block w-full sm:text-sm border-gray-300 rounded-md"
            />
          </div>
          
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700">Email</label>
            <input
              type="email"
              name="email"
              id="email"
              value={letterhead.email}
              onChange={handleInputChange}
              className="mt-1 focus:ring-primary focus:border-primary block w-full sm:text-sm border-gray-300 rounded-md"
            />
          </div>
          
          <div>
            <label htmlFor="website" className="block text-sm font-medium text-gray-700">Website</label>
            <input
              type="text"
              name="website"
              id="website"
              value={letterhead.website}
              onChange={handleInputChange}
              className="mt-1 focus:ring-primary focus:border-primary block w-full sm:text-sm border-gray-300 rounded-md"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700">Firm Logo</label>
            <div className="mt-1 flex items-center">
              {logoPreview ? (
                <div className="relative">
                  <img src={logoPreview} alt="Firm Logo" className="h-16 w-auto object-contain" />
                  <button
                    type="button"
                    onClick={() => {
                      setLogoPreview(null);
                      setLetterhead({
                        ...letterhead,
                        logo: null
                      });
                    }}
                    className="absolute -top-2 -right-2 bg-red-100 rounded-full p-1 text-red-600 hover:bg-red-200"
                  >
                    <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                    </svg>
                  </button>
                </div>
              ) : (
                <div className="flex items-center">
                  <label htmlFor="logo-upload" className="relative cursor-pointer bg-white rounded-md font-medium text-primary hover:text-primary-dark focus-within:outline-none">
                    <span>Upload a file</span>
                    <input id="logo-upload" name="logo-upload" type="file" className="sr-only" onChange={handleLogoUpload} accept="image/*" />
                  </label>
                  <p className="pl-1 text-sm text-gray-500">or drag and drop</p>
                </div>
              )}
            </div>
            <p className="mt-2 text-sm text-gray-500">PNG, JPG, GIF up to 2MB</p>
          </div>
        </div>
        
        <div className="border-t border-gray-200 pt-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Letterhead Preview</h3>
          <div className="border border-gray-300 rounded-lg p-6 bg-white">
            <div className="flex justify-between items-start">
              {logoPreview && (
                <img src={logoPreview} alt="Firm Logo" className="h-16 w-auto object-contain" />
              )}
              <div className={`text-right ${logoPreview ? '' : 'w-full'}`}>
                <h3 className="text-lg font-bold text-gray-900">{letterhead.firmName}</h3>
                <p className="text-sm text-gray-600">{letterhead.address}</p>
                <p className="text-sm text-gray-600">{letterhead.city}, {letterhead.state} {letterhead.zipCode}</p>
                <p className="text-sm text-gray-600">{letterhead.phone} | {letterhead.email}</p>
                <p className="text-sm text-gray-600">{letterhead.website}</p>
              </div>
            </div>
            <div className="mt-6 border-t border-gray-300 pt-6">
              <p className="text-gray-400 italic">Letter content will appear here...</p>
            </div>
          </div>
        </div>
        
        <div className="flex justify-end space-x-3">
          <button
            type="button"
            className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={isSaving}
            className={`px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white ${isSaving ? 'bg-gray-400' : 'bg-primary hover:bg-primary-dark'} focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary`}
          >
            {isSaving ? 'Saving...' : 'Save Letterhead'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default LetterheadSettings;
