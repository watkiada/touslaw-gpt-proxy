import React from 'react';

export default function Chat() {
  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-auto p-4" id="chat-window">
        {/* Messages will appear here */}
      </div>
      <div className="p-4 border-t">
        <input type="text" placeholder="Type your message..." className="w-full p-2 border rounded" />
      </div>
    </div>
  );
}
