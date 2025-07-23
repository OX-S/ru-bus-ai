import React from 'react';
import { MapPinIcon, ClockIcon } from '@heroicons/react/24/outline';
import DirectionStep from './DirectionStep';
import { formatTravelTime } from '../../utils/stringFormatters';

function DirectionsWidget({ from, to, directions, totalTime, walkingTime }) {
  if (!directions || directions.length === 0) {
    return (
      <div className="text-center py-4">
        <MapPinIcon className="w-8 h-8 text-gray-400 mx-auto mb-2" />
        <p className="text-gray-500 font-body text-sm">No directions available</p>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center space-x-2 mb-3">
        <MapPinIcon className="w-5 h-5 text-red-600" />
        <h3 className="font-display text-lg font-bold text-gray-800">
          Transit Directions
        </h3>
      </div>
      
      <div className="bg-gray-50 rounded-lg p-3 mb-4">
        <div className="flex items-center justify-between text-sm">
          <div>
            <p className="text-xs text-gray-600 font-body">From</p>
            <p className="font-body font-medium text-gray-800">{from}</p>
          </div>
          <div className="text-center">
            <div className="flex items-center space-x-1 text-gray-600">
              <ClockIcon className="w-3 h-3" />
              <span className="text-xs font-body">
                {formatTravelTime(totalTime)}
              </span>
            </div>
            {walkingTime && (
              <p className="text-xs text-gray-500 font-body">
                +{walkingTime} min walk
              </p>
            )}
          </div>
          <div className="text-right">
            <p className="text-xs text-gray-600 font-body">To</p>
            <p className="font-body font-medium text-gray-800">{to}</p>
          </div>
        </div>
      </div>
      
      <div className="space-y-1">
        {directions.map((step, index) => (
          <DirectionStep 
            key={index} 
            step={step} 
            isLast={index === directions.length - 1}
          />
        ))}
      </div>
    </div>
  );
}

export default DirectionsWidget;