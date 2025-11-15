// API service helpers for widgets
const API_BASE_URL = 'http://127.0.0.1:8000/v1/v1/widgets';

const handleResponse = async (response, context) => {
  if (!response.ok) {
    throw new Error(`HTTP error while fetching ${context}: ${response.status}`);
  }
  return response.json();
};

export const fetchActiveRoutes = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/active-routes`);
    const data = await handleResponse(response, 'active routes');
    return Array.isArray(data?.routes) ? data.routes : [];
  } catch (error) {
    console.error('Error fetching active routes:', error);
    throw error;
  }
};

export const fetchBusArrivals = async (stopIds, horizonSec = 43200, perStopLimit = 30) => {
  try {
    const response = await fetch(`${API_BASE_URL}/arrivals`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        stop_ids: stopIds,
        horizon_sec: horizonSec,
        per_stop_limit: perStopLimit
      }),
    });

    return handleResponse(response, 'bus arrivals');
  } catch (error) {
    console.error('Error fetching bus arrivals:', error);
    throw error;
  }
};

export const transformArrivalData = (apiResponse) => {
  if (!apiResponse || !apiResponse.stops) {
    return [];
  }

  return apiResponse.stops.map(stop => ({
    stopId: stop.stop_id,
    stopName: stop.stop_name,
    arrivals: stop.arrivals.map(arrival => ({
      route: arrival.route_long_name,
      color: arrival.route_color,
      destination: arrival.to,
      arrivalMinutes: Math.max(0, Math.round(arrival.eta_seconds / 60)),
      etaSeconds: arrival.eta_seconds
    }))
  }));
};
