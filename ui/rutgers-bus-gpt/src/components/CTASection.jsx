import React from 'react';
import { ChatBubbleLeftRightIcon, HeartIcon } from '@heroicons/react/24/outline';

function CTASection({ navigate }) {
  return (
    <section className="py-20 px-6 bg-gradient-to-br from-red-50 to-orange-50">
      <div className="max-w-4xl mx-auto text-center">
        <h2 className="font-display text-4xl md:text-5xl font-bold mb-6" style={{ color: 'var(--color-text-primary)' }}>
          Ready to Transform Your
          <span className="text-gradient block">Campus Experience?</span>
        </h2>
        <p className="text-xl text-gray-600 font-body mb-12 max-w-2xl mx-auto">
          Join thousands of Rutgers students who've already discovered smarter campus navigation
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-6 mb-12">
          <button
            onClick={() => navigate('/chat')}
            className="btn-primary font-body text-xl font-semibold px-10 py-5 rounded-2xl inline-flex items-center space-x-3 shadow-2xl"
          >
            <ChatBubbleLeftRightIcon className="w-6 h-6" />
            <span>Start Your Journey</span>
          </button>
          <a
            href="https://buymeacoffee.com/rutgersbus"
            target="_blank"
            rel="noopener noreferrer"
            className="btn-secondary font-body px-8 py-5 rounded-2xl inline-flex items-center space-x-2"
          >
            <HeartIcon className="w-5 h-5" />
            <span>Support the Project</span>
          </a>
        </div>

        <p className="text-sm text-gray-500 font-body">
          Free to use • No registration required • Privacy focused
        </p>
      </div>
    </section>
  );
}

export default CTASection;