import React from 'react';
import { formatRouteColor, formatArrivalTime, getArrivalStatus } from '../../utils/stringFormatters';

function BusArrivalItem({ arrival }) {
  const getStatusColor = (status) => {
    switch (status) {
      case 'arriving':
        return 'text-red-600 bg-red-50';
      case 'soon':
        return 'text-orange-600 bg-orange-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  const status = getArrivalStatus(arrival.arrivalMinutes);

  return (
    <div className="flex items-center justify-between p-2 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
      <div className="flex items-center space-x-2">
        <div 
          className="w-3 h-3 rounded-full"
          style={{ backgroundColor: formatRouteColor(arrival.color) }}
        />
        <span className="font-body font-medium text-gray-800 text-sm">
          {arrival.route}
        </span>
        {arrival.destination && (
          <span className="text-xs text-gray-500 font-body">
            to {arrival.destination}
          </span>
        )}
      </div>
      
      <div className="flex items-center space-x-2">
        <span 
          className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(status)}`}
        >
          {formatArrivalTime(arrival.arrivalMinutes)}
        </span>
      </div>
    </div>
  );
}

export default BusArrivalItem;