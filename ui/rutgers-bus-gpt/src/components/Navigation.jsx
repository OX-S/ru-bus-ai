import React from 'react';
import { TruckIcon, BugAntIcon, HeartIcon, HomeIcon } from '@heroicons/react/24/outline';

function Navigation({ navigate, showHomeButton = false, showFeedbackButton = true, showSupportButton = true }) {
  return (
    <nav className="nav-premium fixed w-full top-0 z-50 px-6 py-4">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <button
          onClick={() => navigate('/')}
          className="flex items-center space-x-4 group"
        >
          <div className="p-2 bg-gradient-to-br from-red-500 to-red-600 rounded-xl shadow-lg group-hover:shadow-xl transition-all">
            <TruckIcon className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="font-display text-xl font-bold text-gradient">
              RU Bus AI
            </h1>
            <p className="text-xs text-gray-500 font-body">Smart Campus Transit</p>
          </div>
        </button>
        
        <div className="flex items-center space-x-6">
          {showHomeButton && (
            <button
              onClick={() => navigate('/')}
              className="btn-ghost flex items-center space-x-2 px-4 py-2 rounded-lg"
            >
              <HomeIcon className="w-4 h-4" />
              <span className="font-body text-sm font-medium">Home</span>
            </button>
          )}
          
          {showFeedbackButton && (
            <button
              onClick={() => navigate('/bug-reports')}
              className="btn-ghost flex items-center space-x-2 px-4 py-2 rounded-lg"
            >
              <BugAntIcon className="w-4 h-4" />
              <span className="font-body text-sm font-medium">Feedback</span>
            </button>
          )}
          
          {showSupportButton && (
            <a
              href="https://buymeacoffee.com/rutgersbus"
              target="_blank"
              rel="noopener noreferrer"
              className="btn-ghost flex items-center space-x-2 px-4 py-2 rounded-lg"
            >
              <HeartIcon className="w-4 h-4" />
              <span className="font-body text-sm font-medium">Support</span>
            </a>
          )}
        </div>
      </div>
    </nav>
  );
}

export default Navigation;