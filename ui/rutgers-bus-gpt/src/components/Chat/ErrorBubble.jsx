import React from 'react';
import { ExclamationTriangleIcon, ArrowPathIcon } from '@heroicons/react/24/outline';

function ErrorBubble({ message = "Trouble generating response", onRetry }) {
  return (
    <div className="flex items-start space-x-3 mb-6">
      <div className="p-2 rounded-xl shadow-md bg-gradient-to-br from-red-100 to-red-200">
        <ExclamationTriangleIcon className="w-5 h-5 text-red-600" />
      </div>
      
      <div className="flex-1 max-w-xs sm:max-w-md md:max-w-lg">
        <div className="inline-block p-4 rounded-2xl shadow-sm bg-red-50 border border-red-200">
          <div className="flex items-center justify-between">
            <p className="font-body text-sm text-red-800">{message}</p>
            {onRetry && (
              <button
                onClick={onRetry}
                className="ml-3 p-1 text-red-600 hover:text-red-800 transition-colors"
                title="Retry"
              >
                <ArrowPathIcon className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default ErrorBubble;