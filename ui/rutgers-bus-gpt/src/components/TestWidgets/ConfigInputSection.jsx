import React, { useState } from 'react';
import { PlayIcon, XMarkIcon, CogIcon } from '@heroicons/react/24/outline';

function ConfigInputSection({ onConfigSubmit, onClear }) {
  const [configText, setConfigText] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = () => {
    setError('');
    
    if (!configText.trim()) {
      setError('Please enter a JSON configuration');
      return;
    }

    try {
      const parsed = JSON.parse(configText);
      onConfigSubmit(parsed);
    } catch (err) {
      setError('Invalid JSON format. Please check your syntax.');
    }
  };

  const handleClear = () => {
    setConfigText('');
    setError('');
    onClear();
  };

  return (
    <div className="card-premium p-6">
      <div className="flex items-center space-x-3 mb-4">
        <CogIcon className="w-6 h-6 text-red-600" />
        <h2 className="font-display text-xl font-bold text-gray-800">
          JSON Configuration
        </h2>
      </div>
      
      <p className="text-gray-600 font-body mb-4">
        Enter a JSON configuration to test widget rendering:
      </p>
      
      <textarea
        value={configText}
        onChange={(e) => setConfigText(e.target.value)}
        placeholder='{"type": "chat_message", "message": "Hello World!"}'
        className="form-input w-full h-40 resize-none font-mono text-sm"
        style={{ fontFamily: 'Monaco, Consolas, "Courier New", monospace' }}
      />
      
      {error && (
        <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-600 text-sm font-body">
            <strong>Error:</strong> {error}
          </p>
        </div>
      )}
      
      <div className="flex space-x-3 mt-4">
        <button
          onClick={handleSubmit}
          className="btn-primary font-body px-6 py-2 rounded-xl flex items-center space-x-2"
        >
          <PlayIcon className="w-4 h-4" />
          <span>Render</span>
        </button>
        
        <button
          onClick={handleClear}
          className="btn-secondary font-body px-6 py-2 rounded-xl flex items-center space-x-2"
        >
          <XMarkIcon className="w-4 h-4" />
          <span>Clear</span>
        </button>
      </div>
    </div>
  );
}

export default ConfigInputSection;