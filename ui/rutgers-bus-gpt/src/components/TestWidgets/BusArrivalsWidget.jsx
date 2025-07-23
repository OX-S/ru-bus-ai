import React from 'react';
import { ClockIcon, MapPinIcon } from '@heroicons/react/24/outline';
import BusArrivalItem from './BusArrivalItem';

function BusArrivalsWidget({ stopName, arrivals }) {
  if (!arrivals || arrivals.length === 0) {
    return (
      <div className="text-center py-4">
        <ClockIcon className="w-8 h-8 text-gray-400 mx-auto mb-2" />
        <p className="text-gray-500 font-body text-sm">
          No buses stopping at {stopName || 'this stop'}
        </p>
      </div>
    );
  }

  // Sort arrivals by arrival time
  const sortedArrivals = [...arrivals].sort((a, b) => a.arrivalMinutes - b.arrivalMinutes);

  return (
    <div>
      <div className="flex items-center space-x-2 mb-3">
        <ClockIcon className="w-5 h-5 text-red-600" />
        <h3 className="font-display text-lg font-bold text-gray-800">
          Bus Arrivals
        </h3>
      </div>
      
      {stopName && (
        <div className="flex items-center space-x-2 mb-3 p-2 bg-gray-50 rounded-lg">
          <MapPinIcon className="w-4 h-4 text-gray-600" />
          <span className="font-body font-medium text-gray-800 text-sm">
            {stopName}
          </span>
        </div>
      )}
      
      <div className="space-y-2">
        {sortedArrivals.map((arrival, index) => (
          <BusArrivalItem key={index} arrival={arrival} />
        ))}
      </div>
      
      {arrivals.length > 0 && (
        <div className="mt-3 text-center">
          <p className="text-xs text-gray-500 font-body">
            Times are estimates and may vary
          </p>
        </div>
      )}
    </div>
  );
}

export default BusArrivalsWidget;