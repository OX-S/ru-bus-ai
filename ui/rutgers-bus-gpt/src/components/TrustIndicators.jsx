import React from 'react';
import { ShieldCheckIcon, ClockIcon, MapPinIcon } from '@heroicons/react/24/outline';

function TrustIndicators() {
  const indicators = [
    { icon: ShieldCheckIcon, text: "Secure & Private" },
    { icon: ClockIcon, text: "Real-time Updates" },
    { icon: MapPinIcon, text: "Campus-wide Coverage" }
  ];

  return (
    <div className="flex flex-wrap items-center justify-center gap-8 text-sm text-gray-500 font-body">
      {indicators.map((indicator, index) => (
        <div key={index} className="flex items-center space-x-2">
          <indicator.icon className="w-4 h-4" />
          <span>{indicator.text}</span>
        </div>
      ))}
    </div>
  );
}

export default TrustIndicators;