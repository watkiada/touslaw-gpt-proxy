import React from 'react';

export default function Documents() {
  return (
    <div className="p-4 space-y-4">
      <button className="px-4 py-2 bg-blue-500 text-white rounded">Upload File</button>
      {/* File list placeholder */}
      <ul className="space-y-2">
        <li>No files uploaded.</li>
      </ul>
    </div>
  );
}
