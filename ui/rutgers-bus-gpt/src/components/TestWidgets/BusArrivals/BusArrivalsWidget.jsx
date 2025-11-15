import React, { useState, useEffect, useRef } from 'react';
import { ClockIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';
import BusStopSection from './BusStopSection.jsx';
import LoadingSpinner from '../../Chat/LoadingSpinner.jsx';
import { fetchBusArrivals, transformArrivalData } from '../../../utils/apiService.js';

function BusArrivalsWidget({ stopIds }) {
  const [stops, setStops] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const intervalRef = useRef(null);

  const loadArrivals = async (isInitial = false) => {
    try {
      if (isInitial) {
        setLoading(true);
        setError(null);
      }

      const response = await fetchBusArrivals(stopIds);
      const transformedData = transformArrivalData(response);
      
      setStops(transformedData);
      setLastUpdated(new Date());
      setError(null);
      
      if (isInitial) {
        setLoading(false);
      }
    } catch (err) {
      console.error('Error loading bus arrivals:', err);
      setError('Failed to load bus arrivals');
      
      if (isInitial) {
        setLoading(false);
      }
    }
  };

  useEffect(() => {
    if (!stopIds || stopIds.length === 0) {
      setError('No stop IDs provided');
      setLoading(false);
      return;
    }

    // Initial load
    loadArrivals(true);

    // Set up interval for refreshing every 15 seconds
    intervalRef.current = setInterval(() => {
      loadArrivals(false);
    }, 15000);

    // Cleanup interval on unmount
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [stopIds]);

  if (loading) {
    return (
      <div className="py-4">
        <div className="flex items-center space-x-2 mb-3">
          <ClockIcon className="w-5 h-5 text-red-600" />
          <h3 className="font-display text-lg font-bold text-gray-800">
            Bus Arrivals
          </h3>
        </div>
        <div className="flex items-center justify-center py-8">
          <div className="text-center">
            <div className="w-6 h-6 rounded-full border-2 border-gray-300 border-t-red-500 animate-spin mx-auto mb-2"></div>
            <p className="text-sm text-gray-600 font-body">Loading arrivals...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="py-4">
        <div className="flex items-center space-x-2 mb-3">
          <ClockIcon className="w-5 h-5 text-red-600" />
          <h3 className="font-display text-lg font-bold text-gray-800">
            Bus Arrivals
          </h3>
        </div>
        <div className="text-center py-4">
          <ExclamationTriangleIcon className="w-8 h-8 text-red-500 mx-auto mb-2" />
          <p className="text-red-600 font-body text-sm">{error}</p>
        </div>
      </div>
    );
  }

  if (!stops || stops.length === 0) {
    return (
      <div className="py-4">
        <div className="flex items-center space-x-2 mb-3">
          <ClockIcon className="w-5 h-5 text-red-600" />
          <h3 className="font-display text-lg font-bold text-gray-800">
            Bus Arrivals
          </h3>
        </div>
        <div className="text-center py-4">
          <ClockIcon className="w-8 h-8 text-gray-400 mx-auto mb-2" />
          <p className="text-gray-500 font-body text-sm">
            No stops found
          </p>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <ClockIcon className="w-5 h-5 text-red-600" />
          <h3 className="font-display text-lg font-bold text-gray-800">
            Bus Arrivals
          </h3>
        </div>
        {lastUpdated && (
          <span className="text-xs text-gray-500 font-body">
            Updated {lastUpdated.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </span>
        )}
      </div>
      
      <div>
        {stops.map((stop) => (
          <BusStopSection key={stop.stopId} stop={stop} />
        ))}
      </div>
      
      <div className="mt-3 text-center">
        <p className="text-xs text-gray-500 font-body">
          Updates every 15 seconds • Times are estimates
        </p>
      </div>
    </div>
  );
}

export default BusArrivalsWidget;