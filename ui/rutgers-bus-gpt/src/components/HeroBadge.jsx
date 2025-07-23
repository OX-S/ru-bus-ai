import React from 'react';

function HeroBadge({ icon: Icon, text, className = "" }) {
  return (
    <div className={`inline-flex items-center space-x-2 bg-white/80 backdrop-blur-sm border border-red-100 rounded-full px-4 py-2 mb-8 shadow-lg ${className}`}>
      <Icon className="w-4 h-4 text-red-500" />
      <span className="font-body text-sm font-medium text-gray-700">
        {text}
      </span>
    </div>
  );
}

export default HeroBadge;