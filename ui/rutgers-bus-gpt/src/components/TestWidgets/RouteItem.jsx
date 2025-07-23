import React, { useState } from 'react';
import { ChevronDownIcon, ChevronUpIcon } from '@heroicons/react/24/outline';
import { formatRouteColor, formatStopName } from '../../utils/stringFormatters';

function RouteItem({ route }) {
  const [isExpanded, setIsExpanded] = useState(false);

  const toggleExpanded = () => {
    setIsExpanded(!isExpanded);
  };

  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden">
      <button
        onClick={toggleExpanded}
        className="w-full p-2 flex items-center justify-between hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-center space-x-2">
          <div 
            className="w-3 h-3 rounded-full"
            style={{ backgroundColor: formatRouteColor(route.color) }}
          />
          <span className="font-body font-medium text-gray-800 text-sm">
            {route.name}
          </span>
        </div>
        <div className="flex items-center space-x-1">
          <span className="text-xs text-gray-500 font-body">
            {route.stops.length}
          </span>
          {isExpanded ? (
            <ChevronUpIcon className="w-4 h-4 text-gray-400" />
          ) : (
            <ChevronDownIcon className="w-4 h-4 text-gray-400" />
          )}
        </div>
      </button>
      
      {isExpanded && (
        <div className="border-t border-gray-200 bg-gray-50 p-2">
          <div className="space-y-1">
            {route.stops.map((stop, index) => (
              <div key={index} className="flex items-center space-x-2">
                <div className="w-1.5 h-1.5 rounded-full bg-gray-400" />
                <span className="text-xs font-body text-gray-700">
                  {formatStopName(stop)}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default RouteItem;