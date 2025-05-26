import React, { useState } from 'react';

const PDFFormViewer = () => {
  const [formData, setFormData] = useState({
    clientName: 'John Smith',
    caseNumber: 'SMI-2025-0042',
    dateOfBirth: '05/12/1980',
    address: '123 Main Street, Anytown, USA',
    phoneNumber: '(555) 123-4567',
    email: 'john.smith@example.com',
    occupation: 'Software Engineer',
    employerName: 'Tech Solutions Inc.',
    incidentDate: '04/15/2025',
    incidentDescription: 'Automobile accident at intersection of Main St. and 5th Ave.',
    injuries: 'Whiplash, minor contusions',
    witnesses: 'Jane Doe, Officer Michael Johnson',
    insuranceProvider: 'AllState Insurance',
    policyNumber: 'AS-987654321',
    additionalNotes: ''
  });

  const [isAIFilling, setIsAIFilling] = useState(false);
  const [aiSuggestions, setAiSuggestions] = useState({});
  const [showPreview, setShowPreview] = useState(true);

  // Mock function to simulate AI filling the form
  const handleAIFill = () => {
    setIsAIFilling(true);
    
    // Simulate AI processing time
    setTimeout(() => {
      const suggestions = {
        clientName: 'Jonathan A. Smith',
        dateOfBirth: '05/12/1980',
        address: '123 Main Street, Apt 4B, Anytown, CA 94123',
        phoneNumber: '(555) 123-4567',
        email: 'jonathan.smith@example.com',
        occupation: 'Senior Software Engineer',
        employerName: 'Tech Solutions Inc.',
        incidentDate: '04/15/2025',
        incidentDescription: 'Automobile accident at intersection of Main St. and 5th Ave. Client was stopped at red light when rear-ended by another vehicle.',
        injuries: 'Whiplash, minor contusions to left arm, headaches',
        witnesses: 'Jane Doe (pedestrian), Officer Michael Johnson (Badge #4392)',
        insuranceProvider: 'AllState Insurance',
        policyNumber: 'AS-987654321-01',
        additionalNotes: 'Client has previous back injury from 2022. Medical records requested from Dr. Williams.'
      };
      
      setAiSuggestions(suggestions);
      setIsAIFilling(false);
    }, 2000);
  };

  // Handle accepting AI suggestions
  const acceptSuggestion = (field) => {
    setFormData({
      ...formData,
      [field]: aiSuggestions[field]
    });
    
    // Remove the suggestion once accepted
    const newSuggestions = {...aiSuggestions};
    delete newSuggestions[field];
    setAiSuggestions(newSuggestions);
  };

  // Handle form input changes
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-medium text-gray-900">Client Intake Form</h2>
        <div className="flex space-x-2">
          <button 
            onClick={handleAIFill}
            disabled={isAIFilling}
            className={`px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white ${isAIFilling ? 'bg-gray-400' : 'bg-primary hover:bg-primary-dark'} focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary`}
          >
            {isAIFilling ? 'AI Processing...' : 'Auto-Fill with AI'}
          </button>
          <button 
            onClick={() => setShowPreview(!showPreview)}
            className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
          >
            {showPreview ? 'Hide Preview' : 'Show Preview'}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Form Fields */}
        <div className="space-y-6">
          <div>
            <label htmlFor="clientName" className="block text-sm font-medium text-gray-700">Client Name</label>
            <div className="mt-1 relative">
              <input
                type="text"
                name="clientName"
                id="clientName"
                value={formData.clientName}
                onChange={handleInputChange}
                className="focus:ring-primary focus:border-primary block w-full sm:text-sm border-gray-300 rounded-md"
              />
              {aiSuggestions.clientName && (
                <div className="mt-1 p-2 bg-blue-50 border border-blue-200 rounded-md">
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-blue-700">AI suggests: {aiSuggestions.clientName}</span>
                    <button 
                      onClick={() => acceptSuggestion('clientName')}
                      className="text-xs text-blue-700 font-medium hover:text-blue-900"
                    >
                      Accept
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>

          <div>
            <label htmlFor="caseNumber" className="block text-sm font-medium text-gray-700">Case Number</label>
            <input
              type="text"
              name="caseNumber"
              id="caseNumber"
              value={formData.caseNumber}
              onChange={handleInputChange}
              className="mt-1 focus:ring-primary focus:border-primary block w-full sm:text-sm border-gray-300 rounded-md"
            />
          </div>

          <div>
            <label htmlFor="dateOfBirth" className="block text-sm font-medium text-gray-700">Date of Birth</label>
            <input
              type="text"
              name="dateOfBirth"
              id="dateOfBirth"
              value={formData.dateOfBirth}
              onChange={handleInputChange}
              className="mt-1 focus:ring-primary focus:border-primary block w-full sm:text-sm border-gray-300 rounded-md"
            />
            {aiSuggestions.dateOfBirth && (
              <div className="mt-1 p-2 bg-blue-50 border border-blue-200 rounded-md">
                <div className="flex justify-between items-center">
                  <span className="text-xs text-blue-700">AI suggests: {aiSuggestions.dateOfBirth}</span>
                  <button 
                    onClick={() => acceptSuggestion('dateOfBirth')}
                    className="text-xs text-blue-700 font-medium hover:text-blue-900"
                  >
                    Accept
                  </button>
                </div>
              </div>
            )}
          </div>

          <div>
            <label htmlFor="address" className="block text-sm font-medium text-gray-700">Address</label>
            <input
              type="text"
              name="address"
              id="address"
              value={formData.address}
              onChange={handleInputChange}
              className="mt-1 focus:ring-primary focus:border-primary block w-full sm:text-sm border-gray-300 rounded-md"
            />
            {aiSuggestions.address && (
              <div className="mt-1 p-2 bg-blue-50 border border-blue-200 rounded-md">
                <div className="flex justify-between items-center">
                  <span className="text-xs text-blue-700">AI suggests: {aiSuggestions.address}</span>
                  <button 
                    onClick={() => acceptSuggestion('address')}
                    className="text-xs text-blue-700 font-medium hover:text-blue-900"
                  >
                    Accept
                  </button>
                </div>
              </div>
            )}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="phoneNumber" className="block text-sm font-medium text-gray-700">Phone Number</label>
              <input
                type="text"
                name="phoneNumber"
                id="phoneNumber"
                value={formData.phoneNumber}
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
                value={formData.email}
                onChange={handleInputChange}
                className="mt-1 focus:ring-primary focus:border-primary block w-full sm:text-sm border-gray-300 rounded-md"
              />
            </div>
          </div>

          <div>
            <label htmlFor="incidentDescription" className="block text-sm font-medium text-gray-700">Incident Description</label>
            <textarea
              name="incidentDescription"
              id="incidentDescription"
              rows={3}
              value={formData.incidentDescription}
              onChange={handleInputChange}
              className="mt-1 focus:ring-primary focus:border-primary block w-full sm:text-sm border-gray-300 rounded-md"
            />
            {aiSuggestions.incidentDescription && (
              <div className="mt-1 p-2 bg-blue-50 border border-blue-200 rounded-md">
                <div className="flex justify-between items-center">
                  <span className="text-xs text-blue-700">AI suggests: {aiSuggestions.incidentDescription}</span>
                  <button 
                    onClick={() => acceptSuggestion('incidentDescription')}
                    className="text-xs text-blue-700 font-medium hover:text-blue-900"
                  >
                    Accept
                  </button>
                </div>
              </div>
            )}
          </div>

          <div className="flex justify-end space-x-3">
            <button className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary">
              Save Draft
            </button>
            <button className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary">
              Submit Form
            </button>
          </div>
        </div>

        {/* PDF Preview */}
        {showPreview && (
          <div className="border border-gray-200 rounded-lg p-4 bg-gray-50">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Form Preview</h3>
            <div className="bg-white border border-gray-300 rounded-lg p-6 min-h-[600px] shadow-sm">
              <div className="text-center mb-6">
                <h2 className="text-xl font-bold text-gray-900">CLIENT INTAKE FORM</h2>
                <p className="text-sm text-gray-500">Watkibot Law Assistant</p>
              </div>
              
              <div className="space-y-4 text-sm">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="font-medium">Client Name:</p>
                    <p className="border-b border-gray-300 pb-1">{formData.clientName}</p>
                  </div>
                  <div>
                    <p className="font-medium">Case Number:</p>
                    <p className="border-b border-gray-300 pb-1">{formData.caseNumber}</p>
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="font-medium">Date of Birth:</p>
                    <p className="border-b border-gray-300 pb-1">{formData.dateOfBirth}</p>
                  </div>
                  <div>
                    <p className="font-medium">Phone Number:</p>
                    <p className="border-b border-gray-300 pb-1">{formData.phoneNumber}</p>
                  </div>
                </div>
                
                <div>
                  <p className="font-medium">Address:</p>
                  <p className="border-b border-gray-300 pb-1">{formData.address}</p>
                </div>
                
                <div>
                  <p className="font-medium">Email:</p>
                  <p className="border-b border-gray-300 pb-1">{formData.email}</p>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="font-medium">Occupation:</p>
                    <p className="border-b border-gray-300 pb-1">{formData.occupation}</p>
                  </div>
                  <div>
                    <p className="font-medium">Employer:</p>
                    <p className="border-b border-gray-300 pb-1">{formData.employerName}</p>
                  </div>
                </div>
                
                <div>
                  <p className="font-medium">Incident Date:</p>
                  <p className="border-b border-gray-300 pb-1">{formData.incidentDate}</p>
                </div>
                
                <div>
                  <p className="font-medium">Incident Description:</p>
                  <p className="border-b border-gray-300 pb-1">{formData.incidentDescription}</p>
                </div>
                
                <div>
                  <p className="font-medium">Injuries:</p>
                  <p className="border-b border-gray-300 pb-1">{formData.injuries}</p>
                </div>
                
                <div>
                  <p className="font-medium">Witnesses:</p>
                  <p className="border-b border-gray-300 pb-1">{formData.witnesses}</p>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="font-medium">Insurance Provider:</p>
                    <p className="border-b border-gray-300 pb-1">{formData.insuranceProvider}</p>
                  </div>
                  <div>
                    <p className="font-medium">Policy Number:</p>
                    <p className="border-b border-gray-300 pb-1">{formData.policyNumber}</p>
                  </div>
                </div>
                
                <div>
                  <p className="font-medium">Additional Notes:</p>
                  <p className="border-b border-gray-300 pb-1">{formData.additionalNotes}</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PDFFormViewer;
