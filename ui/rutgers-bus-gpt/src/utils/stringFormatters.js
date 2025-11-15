// String formatting functions for widgets
export const formatRouteColor = (color) => {
  // If color is already a hex code, return it
  if (color && color.startsWith('#')) {
    return color;
  }

  // Handle hex strings without the leading hash
  if (typeof color === 'string' && /^[0-9a-fA-F]{6}$/.test(color.trim())) {
    return `#${color.trim()}`;
  }
  
  // Fallback color mapping for named colors
  const colorMap = {
    red: '#dc2626',
    blue: '#2563eb',
    green: '#16a34a',
    yellow: '#ca8a04',
    purple: '#9333ea',
    orange: '#ea580c'
  };
  return colorMap[color] || '#6b7280';
};

export const formatTravelTime = (minutes) => {
  if (minutes < 60) {
    return `${minutes} min`;
  }
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  return remainingMinutes > 0 ? `${hours}h ${remainingMinutes}m` : `${hours}h`;
};

export const formatStopName = (stop) => {
  return stop.charAt(0).toUpperCase() + stop.slice(1).toLowerCase();
};

export const formatArrivalTime = (minutes) => {
  if (minutes === 0) {
    return 'Now';
  }
  if (minutes === 1) {
    return '1 min';
  }
  return `${minutes} min`;
};

export const getArrivalStatus = (minutes) => {
  if (minutes === 0) {
    return 'arriving';
  }
  if (minutes <= 5) {
    return 'soon';
  }
  return 'scheduled';
};
