import React from 'react';
import { ClipboardIcon } from '@heroicons/react/24/outline';

function ExampleConfigCard({ title, config, onCopy }) {
  const handleCopy = () => {
    const configString = JSON.stringify(config, null, 2);
    navigator.clipboard.writeText(configString).then(() => {
      onCopy(configString);
    }).catch(() => {
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = configString;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      onCopy(configString);
    });
  };

  return (
    <div className="border border-gray-200 rounded-xl p-4 hover:border-red-300 transition-colors">
      <div className="flex items-center justify-between mb-3">
        <h4 className="font-body font-semibold text-gray-800">{title}</h4>
        <button
          onClick={handleCopy}
          className="p-2 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
          title="Copy configuration"
        >
          <ClipboardIcon className="w-4 h-4" />
        </button>
      </div>
      
      <pre className="text-xs text-gray-600 bg-gray-50 rounded-lg p-3 overflow-x-auto font-mono">
        {JSON.stringify(config, null, 2)}
      </pre>
    </div>
  );
}

export default ExampleConfigCard;