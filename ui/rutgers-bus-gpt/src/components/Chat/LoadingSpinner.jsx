import React from 'react';

function LoadingSpinner({ message = "Generating response..." }) {
  return (
    <div className="flex items-start space-x-3 mb-6">
      <div className="p-2 rounded-xl shadow-md bg-gradient-to-br from-gray-100 to-gray-200">
        <div className="w-5 h-5 rounded-full border-2 border-gray-300 border-t-red-500 animate-spin"></div>
      </div>
      
      <div className="flex-1 max-w-xs sm:max-w-md md:max-w-lg">
        <div className="inline-block p-4 rounded-2xl shadow-sm bg-white border border-gray-200">
          <div className="flex items-center space-x-2">
            <div className="flex space-x-1">
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
            </div>
            <p className="font-body text-sm text-gray-600">{message}</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default LoadingSpinner;