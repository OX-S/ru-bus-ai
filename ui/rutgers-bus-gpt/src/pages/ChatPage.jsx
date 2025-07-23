import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ChatBubbleLeftRightIcon } from '@heroicons/react/24/outline';
import Navigation from '../components/Navigation';
import HeroBadge from '../components/HeroBadge';
import ChatContainer from '../components/Chat/ChatContainer';

function ChatPage() {
  const navigate = useNavigate();
  return (
    <div className="min-h-screen">
      <Navigation showHomeButton={true} showFeedbackButton={false} showSupportButton={false} />

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

          {/* Chat Interface */}
          <ChatContainer />

          {/* Navigation Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 mt-8 max-w-md mx-auto">
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
      </main>
    </div>
  );
}

export default ChatPage;