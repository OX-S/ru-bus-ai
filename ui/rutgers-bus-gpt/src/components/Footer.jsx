import React from 'react';
import { TruckIcon } from '@heroicons/react/24/outline';

function Footer({ navigate }) {
  return (
    <footer className="bg-white border-t border-gray-100 px-6 py-12">
      <div className="max-w-7xl mx-auto">
        <div className="flex flex-col md:flex-row items-center justify-between">
          <div className="flex items-center space-x-4 mb-6 md:mb-0">
            <div className="p-2 bg-gradient-to-br from-red-500 to-red-600 rounded-xl shadow-lg">
              <TruckIcon className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="font-display text-lg font-bold text-gradient">RU Bus AI</h3>
              <p className="text-sm text-gray-500 font-body">Smart Campus Transit</p>
            </div>
          </div>
          <div className="flex items-center space-x-8">
            <button
              onClick={() => navigate('/bug-reports')}
              className="text-gray-600 hover:text-red-600 font-body text-sm transition-colors"
            >
              Report Issues
            </button>
            <a
              href="https://buymeacoffee.com/rutgersbus"
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-600 hover:text-red-600 font-body text-sm transition-colors"
            >
              Support Us
            </a>
          </div>
        </div>
        <div className="border-t border-gray-100 mt-8 pt-8 text-center">
          <p className="font-body text-gray-500 text-sm">
            Made with ❤️ for Rutgers students • Not affiliated with Rutgers University
          </p>
        </div>
      </div>
    </footer>
  );
}

export default Footer;