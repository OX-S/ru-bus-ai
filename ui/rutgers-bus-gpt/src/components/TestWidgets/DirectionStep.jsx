import React from 'react';
import { formatRouteColor } from '../../utils/stringFormatters';

function DirectionStep({ step, isLast }) {
  const getStepIcon = () => {
    switch (step.action) {
      case 'Take':
        return (
          <div className="w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center">
            <span className="text-xs font-bold text-blue-600">{step.step}</span>
          </div>
        );
      case 'Transfer at':
        return (
          <div className="w-6 h-6 rounded-full bg-yellow-100 flex items-center justify-center">
            <span className="text-xs font-bold text-yellow-600">T</span>
          </div>
        );
      case 'Walk to':
        return (
          <div className="w-6 h-6 rounded-full bg-green-100 flex items-center justify-center">
            <span className="text-xs font-bold text-green-600">W</span>
          </div>
        );
      case 'Arrive at':
        return (
          <div className="w-6 h-6 rounded-full bg-red-100 flex items-center justify-center">
            <span className="text-xs font-bold text-red-600">A</span>
          </div>
        );
      default:
        return (
          <div className="w-6 h-6 rounded-full bg-gray-100 flex items-center justify-center">
            <span className="text-xs font-bold text-gray-600">{step.step}</span>
          </div>
        );
    }
  };

  return (
    <div className="flex items-start space-x-3">
      <div className="flex flex-col items-center">
        {getStepIcon()}
        {!isLast && (
          <div className="w-0.5 h-6 bg-gray-300 mt-1" />
        )}
      </div>
      
      <div className="flex-1 pb-3">
        <div className="flex items-center space-x-2 mb-1">
          <span className="font-body font-medium text-gray-800 text-sm">
            {step.action}
          </span>
          {step.route && (
            <span 
              className="px-1.5 py-0.5 rounded-full text-xs font-bold text-white"
              style={{ backgroundColor: formatRouteColor(step.color) }}
            >
              {step.route}
            </span>
          )}
        </div>
        
        <div className="text-xs text-gray-600 font-body">
          {step.action === 'Take' && (
            <span>From {step.from} to {step.to}</span>
          )}
          {step.action === 'Transfer at' && (
            <span>
              {step.location}
              {step.waitTime && ` (${step.waitTime} min)`}
            </span>
          )}
          {step.action === 'Walk to' && (
            <span>{step.location}</span>
          )}
          {step.action === 'Arrive at' && (
            <span>{step.location}</span>
          )}
        </div>
      </div>
    </div>
  );
}

export default DirectionStep;