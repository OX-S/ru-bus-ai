import React, { useState } from 'react';
import { PaperAirplaneIcon } from '@heroicons/react/24/outline';

function ChatInput({ onSendMessage, disabled = false, placeholder = "Ask me about Rutgers bus routes..." }) {
  const [message, setMessage] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSendMessage(message.trim());
      setMessage('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="relative">
      <textarea
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyPress={handleKeyPress}
        placeholder={placeholder}
        disabled={disabled}
        rows={1}
        className="form-input w-full pr-16 font-body resize-none min-h-[3rem] max-h-32 overflow-y-auto disabled:opacity-50 disabled:cursor-not-allowed"
        style={{
          scrollbarWidth: 'thin',
          scrollbarColor: 'var(--color-border) transparent'
        }}
      />
      <button
        type="submit"
        disabled={disabled || !message.trim()}
        className="absolute right-3 top-1/2 transform -translate-y-1/2 p-2 bg-gradient-to-br from-red-500 to-red-600 rounded-lg shadow-lg disabled:opacity-50 disabled:cursor-not-allowed hover:from-red-600 hover:to-red-700 transition-all duration-200"
      >
        <PaperAirplaneIcon className="w-4 h-4 text-white" />
      </button>
    </form>
  );
}

export default ChatInput;