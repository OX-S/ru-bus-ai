import React, { useCallback, useEffect, useRef, useState } from 'react';
import { TruckIcon } from '@heroicons/react/24/outline';
import RouteItem from './RouteItem.jsx';
import { fetchActiveRoutes } from '../../../utils/apiService.js';

const TEN_MINUTES_MS = 10 * 60 * 1000;

function ActiveRoutesWidget({ routes: initialRoutes = [] }) {
  const [routes, setRoutes] = useState(initialRoutes);
  const [loading, setLoading] = useState(!initialRoutes || initialRoutes.length === 0);
  const [error, setError] = useState(null);

  const intervalRef = useRef(null);
  const routesRef = useRef(initialRoutes);
  const isMountedRef = useRef(false);
  const isFetchingRef = useRef(false);

  useEffect(() => {
    routesRef.current = routes;
  }, [routes]);

  useEffect(() => {
    if (initialRoutes && initialRoutes.length > 0) {
      setRoutes(initialRoutes);
      routesRef.current = initialRoutes;
      setLoading(false);
      setError(null);
    }
  }, [initialRoutes]);

  const loadRoutes = useCallback(async (isInitial = false) => {
    if (isFetchingRef.current || !isMountedRef.current) {
      return;
    }

    const hasRoutes = Array.isArray(routesRef.current) && routesRef.current.length > 0;
    const shouldShowSpinner = isInitial && !hasRoutes;

    if (shouldShowSpinner) {
      setLoading(true);
      setError(null);
    }

    isFetchingRef.current = true;
    try {
      const data = await fetchActiveRoutes();
      if (!isMountedRef.current) {
        return;
      }
      setRoutes(data);
      routesRef.current = data;
      setError(null);
      if (shouldShowSpinner) {
        setLoading(false);
      }
    } catch (err) {
      if (!isMountedRef.current) {
        return;
      }
      console.error('Failed to load active routes:', err);
      setError('Failed to load active routes');
      if (shouldShowSpinner) {
        setLoading(false);
      }
    } finally {
      isFetchingRef.current = false;
    }
  }, []);

  useEffect(() => {
    isMountedRef.current = true;
    loadRoutes(true).then();
    intervalRef.current = setInterval(() => loadRoutes(false), TEN_MINUTES_MS);

    return () => {
      isMountedRef.current = false;
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [loadRoutes]);

  if (loading) {
    return (
      <div className="text-center py-4">
        <TruckIcon className="w-8 h-8 text-red-600 mx-auto mb-2 animate-spin" />
        <p className="text-gray-500 font-body text-sm">Loading active routes...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-4">
        <TruckIcon className="w-8 h-8 text-gray-400 mx-auto mb-2" />
        <p className="text-red-600 font-body text-sm">{error}</p>
      </div>
    );
  }

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
