import React from 'react';
import { useNavigate } from 'react-router-dom';
import { SparklesIcon, ChatBubbleLeftRightIcon, RocketLaunchIcon, ArrowRightIcon } from '@heroicons/react/24/outline';
import HeroBadge from './HeroBadge';
import TrustIndicators from './TrustIndicators';

function HeroSection() {
  const navigate = useNavigate();
  return (
    <section className="hero-bg pt-24 pb-16 px-6">
      <div className="max-w-7xl mx-auto">
        <div className="text-center max-w-4xl mx-auto mb-16">
          {/* Hero Badge */}
          <HeroBadge 
            icon={SparklesIcon}
            text="AI-Powered Campus Navigation"
          />

          {/* Hero Title */}
          <h1 className="text-hero font-display font-bold mb-6">
            Navigate Rutgers
            <span className="text-gradient block">Like Never Before</span>
          </h1>

          {/* Hero Subtitle */}
          <p className="text-subtitle font-body max-w-3xl mx-auto mb-12 leading-relaxed">
            Experience the future of campus transportation with our AI assistant.
            Get instant, intelligent answers about bus routes, real-time schedules,
            and smart navigation tailored for Rutgers students.
          </p>

          {/* Hero CTA */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
            <button
              onClick={() => navigate('/chat')}
              className="btn-primary font-body text-lg font-semibold px-8 py-4 rounded-2xl inline-flex items-center space-x-3 shadow-xl animate-pulse-glow"
            >
              <ChatBubbleLeftRightIcon className="w-6 h-6" />
              <span>Start Conversation</span>
              <ArrowRightIcon className="w-5 h-5" />
            </button>
            <button className="btn-secondary font-body px-6 py-4 rounded-2xl inline-flex items-center space-x-2">
              <RocketLaunchIcon className="w-5 h-5" />
              <span>Watch Demo</span>
            </button>
          </div>

          {/* Trust Indicators */}
          <TrustIndicators />
        </div>
      </div>
    </section>
  );
}

export default HeroSection;