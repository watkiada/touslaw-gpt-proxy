import React from 'react';

export default function Settings() {
  return (
    <div className="p-4 space-y-4">
      <label className="block">
        API Key
        <input type="text" className="mt-1 p-2 border rounded w-full" />
      </label>
      <label className="flex items-center space-x-2">
        <input type="checkbox" />
        <span>Enable Notifications</span>
      </label>
    </div>
  );
}
