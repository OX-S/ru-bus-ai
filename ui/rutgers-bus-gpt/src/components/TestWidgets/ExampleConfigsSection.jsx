import React from 'react';
import { LightBulbIcon } from '@heroicons/react/24/outline';
import ExampleConfigCard from './ExampleConfigCard';
import { mockExampleConfigs } from '../../data/testWidgetsMockData';

function ExampleConfigsSection({ onConfigSelect }) {
  const handleCopyConfig = (configString) => {
    onConfigSelect(configString);
  };

  const getConfigTitle = (config) => {
    switch (config.type) {
      case 'chat_message':
        return 'Chat Message';
      case 'active_routes':
        return 'Active Routes Widget';
      case 'directions':
        return 'Directions Widget';
      case 'bus_arrivals':
        return 'Bus Arrivals Widget (Live API)';
      default:
        return 'Unknown Widget';
    }
  };

  return (
    <div className="card-premium p-6">
      <div className="flex items-center space-x-3 mb-6">
        <LightBulbIcon className="w-6 h-6 text-red-600" />
        <h2 className="font-display text-xl font-bold text-gray-800">
          Example Configurations
        </h2>
      </div>
      
      <p className="text-gray-600 font-body mb-6">
        Try these example configurations to see different widget types:
      </p>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {mockExampleConfigs.map((config, index) => (
          <ExampleConfigCard
            key={index}
            title={getConfigTitle(config)}
            config={config}
            onCopy={handleCopyConfig}
          />
        ))}
      </div>
    </div>
  );
}

export default ExampleConfigsSection;