import React from 'react';
import { MapPinIcon } from '@heroicons/react/24/outline';
import BusArrivalItem from './BusArrivalItem.jsx';

function BusStopSection({ stop }) {
  if (!stop.arrivals || stop.arrivals.length === 0) {
    return (
      <div className="border border-gray-200 rounded-lg p-3 mb-3">
        <div className="flex items-center space-x-2 mb-2">
          <MapPinIcon className="w-4 h-4 text-gray-600" />
          <span className="font-body font-medium text-gray-800 text-sm">
            {stop.stopName}
          </span>
        </div>
        <p className="text-gray-500 font-body text-xs text-center py-2">
          No buses arriving at this stop
        </p>
      </div>
    );
  }

  // Sort arrivals by arrival time
  const sortedArrivals = [...stop.arrivals].sort((a, b) => a.arrivalMinutes - b.arrivalMinutes);

  return (
    <div className="border border-gray-200 rounded-lg p-3 mb-3">
      <div className="flex items-center space-x-2 mb-3">
        <MapPinIcon className="w-4 h-4 text-gray-600" />
        <span className="font-body font-medium text-gray-800 text-sm">
          {stop.stopName}
        </span>
      </div>
      
      <div className="space-y-2">
        {sortedArrivals.map((arrival, index) => (
          <BusArrivalItem key={`${arrival.route}-${arrival.arrivalMinutes}-${index}`} arrival={arrival} />
        ))}
      </div>
    </div>
  );
}

export default BusStopSection;