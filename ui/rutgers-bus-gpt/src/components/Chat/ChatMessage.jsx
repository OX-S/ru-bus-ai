import React from 'react';
import { UserIcon, ChatBubbleLeftRightIcon } from '@heroicons/react/24/outline';

function ChatMessage({ message, isUser, timestamp }) {
  return (
    <div className={`flex items-start space-x-3 mb-6 ${isUser ? 'flex-row-reverse space-x-reverse' : ''}`}>
      <div className={`p-2 rounded-xl shadow-md ${
        isUser 
          ? 'bg-gradient-to-br from-red-500 to-red-600' 
          : 'bg-gradient-to-br from-gray-100 to-gray-200'
      }`}>
        {isUser ? (
          <UserIcon className="w-5 h-5 text-white" />
        ) : (
          <ChatBubbleLeftRightIcon className="w-5 h-5 text-gray-600" />
        )}
      </div>
      
      <div className={`flex-1 max-w-xs sm:max-w-md md:max-w-lg ${isUser ? 'text-right' : ''}`}>
        <div className={`inline-block p-4 rounded-2xl shadow-sm ${
          isUser 
            ? 'bg-gradient-to-br from-red-500 to-red-600 text-white' 
            : 'bg-white border border-gray-200'
        }`}>
          <p className={`font-body text-sm leading-relaxed ${
            isUser ? 'text-white' : 'text-gray-800'
          }`}>
            {message}
          </p>
        </div>
        
        {timestamp && (
          <p className={`text-xs text-gray-500 mt-1 font-body ${isUser ? 'text-right' : ''}`}>
            {new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </p>
        )}
      </div>
    </div>
  );
}

export default ChatMessage;