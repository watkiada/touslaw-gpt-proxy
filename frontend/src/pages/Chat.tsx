import React, { useState } from 'react';

const Chat = () => {
  const [message, setMessage] = useState('');
  const [chatHistory, setChatHistory] = useState([
    { role: 'assistant', content: 'Hello! I\'m your Watkibot Law Assistant. How can I help you today? I can help you fill out forms, organize documents, or answer questions about your cases.' },
    { role: 'user', content: 'I need help filling out the client intake form for the Smith case.' },
    { role: 'assistant', content: 'I\'d be happy to help you fill out the client intake form. I\'ll analyze the documents in the Smith case folder to extract the relevant information. Would you like me to open the form now and start filling it out?' }
  ]);
  
  const [isProcessing, setIsProcessing] = useState(false);
  
  // Handle sending a new message
  const handleSendMessage = () => {
    if (!message.trim()) return;
    
    // Add user message to chat
    const newChatHistory = [
      ...chatHistory,
      { role: 'user', content: message }
    ];
    setChatHistory(newChatHistory);
    setMessage('');
    
    // Simulate AI processing
    setIsProcessing(true);
    
    // Mock AI response after a delay
    setTimeout(() => {
      let aiResponse;
      
      // Simple response logic based on message content
      if (message.toLowerCase().includes('form')) {
        aiResponse = 'I can help with that form. I\'ve analyzed the case documents and found several key details that can be auto-filled. Would you like me to show you a preview of the form with the information I\'ve gathered?';
      } else if (message.toLowerCase().includes('letter')) {
        aiResponse = 'I can draft a letter using your firm\'s letterhead. What type of letter do you need? I can prepare demand letters, client communications, or court correspondence based on the case information.';
      } else if (message.toLowerCase().includes('document') || message.toLowerCase().includes('file')) {
        aiResponse = 'I\'ve organized the case documents for you. There are 12 documents in this case, including 3 client statements, 2 police reports, and 4 medical records. Would you like me to summarize any specific document?';
      } else {
        aiResponse = 'I understand. Based on the Smith case documents, I can help you with form filling, document organization, or drafting correspondence. What specific aspect would you like assistance with?';
      }
      
      // Add AI response to chat
      setChatHistory([
        ...newChatHistory,
        { role: 'assistant', content: aiResponse }
      ]);
      
      setIsProcessing(false);
    }, 1500);
  };
  
  // Handle pressing Enter to send message
  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };
  
  return (
    <div className="bg-white shadow rounded-lg p-6">
      <h2 className="text-xl font-medium text-gray-900 mb-6">AI Assistant Chat</h2>
      
      <div className="border border-gray-200 rounded-lg h-[600px] flex flex-col">
        {/* Chat messages */}
        <div className="flex-1 p-4 overflow-y-auto space-y-4">
          {chatHistory.map((chat, index) => (
            chat.role === 'assistant' ? (
              // AI message
              <div key={index} className="flex items-start">
                <div className="flex-shrink-0">
                  <div className="h-10 w-10 rounded-full bg-primary flex items-center justify-center text-white">
                    AI
                  </div>
                </div>
                <div className="ml-3 bg-gray-100 rounded-lg py-2 px-4 max-w-3xl">
                  <p className="text-sm text-gray-900">{chat.content}</p>
                </div>
              </div>
            ) : (
              // User message
              <div key={index} className="flex items-start justify-end">
                <div className="bg-primary rounded-lg py-2 px-4 max-w-3xl">
                  <p className="text-sm text-white">{chat.content}</p>
                </div>
                <div className="ml-3 flex-shrink-0">
                  <div className="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center text-gray-700">
                    You
                  </div>
                </div>
              </div>
            )
          ))}
          
          {/* Processing indicator */}
          {isProcessing && (
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <div className="h-10 w-10 rounded-full bg-primary flex items-center justify-center text-white">
                  AI
                </div>
              </div>
              <div className="ml-3 bg-gray-100 rounded-lg py-2 px-4">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                </div>
              </div>
            </div>
          )}
        </div>
        
        {/* Message input */}
        <div className="border-t border-gray-200 p-4">
          <div className="flex space-x-3">
            <textarea
              rows={3}
              className="flex-1 focus:ring-primary focus:border-primary block w-full min-w-0 rounded-md sm:text-sm border-gray-300"
              placeholder="Type your message..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={handleKeyPress}
            />
            <div className="flex flex-col justify-end">
              <button 
                onClick={handleSendMessage}
                disabled={isProcessing || !message.trim()}
                className={`inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white ${isProcessing || !message.trim() ? 'bg-gray-400' : 'bg-primary hover:bg-primary-dark'} focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary`}
              >
                Send
              </button>
            </div>
          </div>
          
          <div className="mt-2 flex space-x-2">
            <button className="inline-flex items-center px-3 py-1 border border-gray-300 rounded-md text-xs font-medium text-gray-700 bg-white hover:bg-gray-50">
              <svg className="mr-1 h-4 w-4 text-gray-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8 4a3 3 0 00-3 3v4a3 3 0 006 0V7a1 1 0 112 0v4a5 5 0 01-10 0V7a5 5 0 0110 0v1.5a1.5 1.5 0 01-3 0V7a1 1 0 012 0v1.5a.5.5 0 001 0V7a3 3 0 00-6 0v4a3 3 0 006 0V7a1 1 0 112 0v4a5 5 0 01-10 0V7a5 5 0 0110 0v1.5a1.5 1.5 0 01-3 0V7a1 1 0 012 0v1.5a.5.5 0 001 0V7a3 3 0 00-6 0v4a3 3 0 006 0V7a1 1 0 112 0v4a5 5 0 01-10 0V7a5 5 0 0110 0v1.5a1.5 1.5 0 01-3 0V7a1 1 0 012 0v1.5a.5.5 0 001 0V7a3 3 0 00-6 0v4a3 3 0 006 0v1.5a.5.5 0 001 0V7a1 1 0 012 0v4a5 5 0 01-10 0V7a5 5 0 0110 0v1.5a1.5 1.5 0 01-3 0V7a1 1 0 012 0v1.5a.5.5 0 001 0V7a3 3 0 00-3-3z" clipRule="evenodd" />
              </svg>
              Attach File
            </button>
            <button className="inline-flex items-center px-3 py-1 border border-gray-300 rounded-md text-xs font-medium text-gray-700 bg-white hover:bg-gray-50">
              <svg className="mr-1 h-4 w-4 text-gray-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clipRule="evenodd" />
              </svg>
              Fill Form
            </button>
            <button className="inline-flex items-center px-3 py-1 border border-gray-300 rounded-md text-xs font-medium text-gray-700 bg-white hover:bg-gray-50">
              <svg className="mr-1 h-4 w-4 text-gray-500" fill="currentColor" viewBox="0 0 20 20">
                <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
              </svg>
              Draft Letter
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chat;
