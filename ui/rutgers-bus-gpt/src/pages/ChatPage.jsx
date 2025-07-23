import React from 'react';
import { ChatBubbleLeftRightIcon, ArrowRightIcon } from '@heroicons/react/24/outline';
import Navigation from '../components/Navigation';
import HeroBadge from '../components/HeroBadge';

function ChatPage({ navigate }) {
  return (
    <div className="min-h-screen">
      <Navigation navigate={navigate} showHomeButton={true} showFeedbackButton={false} showSupportButton={false} />

      {/* Chat Interface */}
      <main className="pt-24 pb-16 px-6 min-h-screen hero-bg">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <HeroBadge 
              icon={ChatBubbleLeftRightIcon}
              text="AI Chat Interface"
            />

            <h1 className="font-display text-4xl md:text-5xl font-bold mb-6" style={{ color: 'var(--color-text-primary)' }}>
              Chat with Your
              <span className="text-gradient block">Campus Navigator</span>
            </h1>
            <p className="text-xl text-gray-600 font-body max-w-2xl mx-auto mb-12">
              Ask me anything about Rutgers bus routes, schedules, and campus navigation. I'm here to help!
            </p>
          </div>

          {/* Chat Container */}
          <div className="glass-card rounded-3xl p-8 md:p-12 max-w-3xl mx-auto">
            <div className="bg-gradient-to-br from-red-50 to-orange-50 rounded-2xl p-8 mb-8 border border-red-100">
              <div className="flex items-start space-x-4">
                <div className="p-3 bg-gradient-to-br from-red-500 to-red-600 rounded-xl shadow-lg">
                  <ChatBubbleLeftRightIcon className="w-6 h-6 text-white" />
                </div>
                <div className="flex-1">
                  <h3 className="font-display text-lg font-bold mb-3" style={{ color: 'var(--color-text-primary)' }}>
                    💬 Chat Interface Coming Soon!
                  </h3>
                  <p className="font-body text-gray-700 mb-4">
                    I'm being trained to help you with:
                  </p>
                  <ul className="font-body space-y-3 text-gray-600">
                    <li className="flex items-center space-x-3">
                      <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                      <span>Real-time bus schedules and delays</span>
                    </li>
                    <li className="flex items-center space-x-3">
                      <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                      <span>Optimal route planning between campuses</span>
                    </li>
                    <li className="flex items-center space-x-3">
                      <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                      <span>Stop locations and walking directions</span>
                    </li>
                    <li className="flex items-center space-x-3">
                      <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                      <span>Service alerts and alternative routes</span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>

            {/* Mock Chat Input */}
            <div className="space-y-4">
              <div className="relative">
                <input
                  type="text"
                  placeholder="Ask me about Rutgers bus routes..."
                  className="form-input w-full pr-16 font-body"
                  disabled
                />
                <button className="absolute right-3 top-1/2 transform -translate-y-1/2 p-2 bg-gradient-to-br from-red-500 to-red-600 rounded-lg shadow-lg">
                  <ArrowRightIcon className="w-4 h-4 text-white" />
                </button>
              </div>

              <div className="flex flex-col sm:flex-row gap-4">
                <button
                  onClick={() => navigate('/')}
                  className="btn-primary font-body px-6 py-3 rounded-xl flex-1"
                >
                  Back to Home
                </button>
                <button
                  onClick={() => navigate('/bug-reports')}
                  className="btn-secondary font-body px-6 py-3 rounded-xl flex-1"
                >
                  Report Feedback
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default ChatPage;