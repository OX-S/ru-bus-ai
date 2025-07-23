import React from 'react';
import { TruckIcon } from '@heroicons/react/24/outline';
import RouteItem from './RouteItem';

function ActiveRoutesWidget({ routes }) {
  if (!routes || routes.length === 0) {
    return (
      <div className="text-center py-4">
        <TruckIcon className="w-8 h-8 text-gray-400 mx-auto mb-2" />
        <p className="text-gray-500 font-body text-sm">No routes available</p>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center space-x-2 mb-3">
        <TruckIcon className="w-5 h-5 text-red-600" />
        <h3 className="font-display text-lg font-bold text-gray-800">
          Active Routes
        </h3>
      </div>
      
      <div className="space-y-2">
        {routes.map((route) => (
          <RouteItem key={route.id} route={route} />
        ))}
      </div>
    </div>
  );
}

export default ActiveRoutesWidget;