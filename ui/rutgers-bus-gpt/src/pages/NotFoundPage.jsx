import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ExclamationTriangleIcon, HomeIcon, ChatBubbleLeftRightIcon } from '@heroicons/react/24/outline';
import Navigation from '../components/Navigation';

function NotFoundPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen">
      <Navigation showHomeButton={false} showFeedbackButton={false} showSupportButton={false} />

      {/* 404 Content */}
      <main className="pt-24 pb-16 px-6 min-h-screen hero-bg flex items-center justify-center">
        <div className="max-w-2xl mx-auto text-center">
          <div className="mb-8">
            <div className="w-24 h-24 bg-gradient-to-br from-red-500 to-red-600 rounded-3xl flex items-center justify-center mx-auto mb-8 shadow-2xl animate-float">
              <ExclamationTriangleIcon className="w-12 h-12 text-white" />
            </div>

            <h1 className="font-display text-8xl md:text-9xl font-bold text-gradient mb-4">404</h1>
            <h2 className="font-display text-3xl md:text-4xl font-bold mb-6" style={{ color: 'var(--color-text-primary)' }}>
              Route Not Found
            </h2>
            <p className="text-xl text-gray-600 font-body mb-12 max-w-lg mx-auto">
              Looks like this page took the wrong bus route! Let's get you back on track to your destination.
            </p>
          </div>

          <div className="glass-card rounded-3xl p-8 mb-8">
            <h3 className="font-display text-xl font-bold mb-6" style={{ color: 'var(--color-text-primary)' }}>
              Quick Navigation
            </h3>
            <div className="grid sm:grid-cols-2 gap-4">
              <button
                onClick={() => navigate('/')}
                className="btn-primary font-body px-6 py-4 rounded-xl inline-flex items-center justify-center space-x-2"
              >
                <HomeIcon className="w-5 h-5" />
                <span>Back to Home</span>
              </button>
              <button
                onClick={() => navigate('/chat')}
                className="btn-secondary font-body px-6 py-4 rounded-xl inline-flex items-center justify-center space-x-2"
              >
                <ChatBubbleLeftRightIcon className="w-5 h-5" />
                <span>Start Chat</span>
              </button>
            </div>
          </div>

          <p className="font-body text-gray-500 text-sm">
            Still having trouble? <button onClick={() => navigate('/bug-reports')} className="text-red-600 hover:text-red-700 font-medium">Report an issue</button>
          </p>
        </div>
      </main>
    </div>
  );
}

export default NotFoundPage;