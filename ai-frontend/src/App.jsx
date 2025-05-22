import React, { useState } from 'react';
import Chat from './components/Chat';
import Documents from './components/Documents';
import Settings from './components/Settings';
import Sidebar from './components/Sidebar';

export default function App() {
  const [view, setView] = useState('chat');

  let content;
  if (view === 'documents') content = <Documents />;
  else if (view === 'settings') content = <Settings />;
  else content = <Chat />;

  return (
    <div className="flex h-screen">
      <Sidebar view={view} setView={setView} />
      <div className="flex-1 overflow-hidden">{content}</div>
    </div>
  );
}
