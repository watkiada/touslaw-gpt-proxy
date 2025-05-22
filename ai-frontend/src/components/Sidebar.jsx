import React from 'react';

export default function Sidebar({ view, setView }) {
  return (
    <div className="w-48 bg-gray-800 text-white flex flex-col p-4 space-y-4">
      <button className={view==='chat' ? 'font-bold' : ''} onClick={() => setView('chat')}>Chat</button>
      <button className={view==='documents' ? 'font-bold' : ''} onClick={() => setView('documents')}>Documents</button>
      <button className={view==='settings' ? 'font-bold' : ''} onClick={() => setView('settings')}>Settings</button>
    </div>
  );
}
