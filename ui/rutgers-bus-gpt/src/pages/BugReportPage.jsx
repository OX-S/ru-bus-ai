import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { BugAntIcon, ChatBubbleLeftRightIcon, HeartIcon } from '@heroicons/react/24/outline';
import Navigation from '../components/Navigation';
import HeroBadge from '../components/HeroBadge';

function BugReportPage() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    email: ''
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    alert('Thank you for your feedback! We\'ll review it carefully.');
    setFormData({ title: '', description: '', email: '' });
  };

  return (
    <div className="min-h-screen">
      <Navigation showHomeButton={true} showFeedbackButton={false} showSupportButton={false} />

      {/* Bug Report Form */}
      <main className="pt-24 pb-16 px-6 min-h-screen hero-bg">
        <div className="max-w-3xl mx-auto">
          <div className="text-center mb-12">
            <HeroBadge 
              icon={BugAntIcon}
              text="Feedback & Bug Reports"
            />

            <h1 className="font-display text-4xl md:text-5xl font-bold mb-6" style={{ color: 'var(--color-text-primary)' }}>
              Help Us
              <span className="text-gradient block">Improve</span>
            </h1>
            <p className="text-xl text-gray-600 font-body max-w-2xl mx-auto">
              Your feedback helps us build a better experience for all Rutgers students
            </p>
          </div>

          <div className="glass-card rounded-3xl p-8 md:p-12">
            <form onSubmit={handleSubmit} className="space-y-8">
              <div>
                <label className="block font-body text-sm font-semibold mb-3" style={{ color: 'var(--color-text-primary)' }}>
                  Issue Title *
                </label>
                <input
                  type="text"
                  required
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  className="form-input w-full font-body"
                  placeholder="Brief description of the issue or suggestion"
                />
              </div>

              <div>
                <label className="block font-body text-sm font-semibold mb-3" style={{ color: 'var(--color-text-primary)' }}>
                  Detailed Description *
                </label>
                <textarea
                  required
                  rows={6}
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="form-input w-full font-body resize-none"
                  placeholder="Please provide detailed information about the issue, steps to reproduce, or your suggestion for improvement..."
                />
              </div>

              <div>
                <label className="block font-body text-sm font-semibold mb-3" style={{ color: 'var(--color-text-primary)' }}>
                  Email (optional)
                </label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="form-input w-full font-body"
                  placeholder="your.email@rutgers.edu"
                />
                <p className="text-sm text-gray-500 font-body mt-2">
                  We'll only use this to follow up on your feedback if needed
                </p>
              </div>

              <div className="flex flex-col sm:flex-row gap-4 pt-4">
                <button
                  type="submit"
                  className="btn-primary font-body text-lg font-semibold px-8 py-4 rounded-xl flex-1 inline-flex items-center justify-center space-x-2"
                >
                  <BugAntIcon className="w-5 h-5" />
                  <span>Submit Feedback</span>
                </button>
                <button
                  type="button"
                  onClick={() => navigate('/')}
                  className="btn-secondary font-body px-8 py-4 rounded-xl flex-1"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>

          {/* Additional Help */}
          <div className="mt-12 text-center">
            <p className="font-body text-gray-600 mb-4">
              Need immediate help? Try these resources:
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <button
                onClick={() => navigate('/chat')}
                className="btn-ghost px-6 py-3 rounded-lg inline-flex items-center space-x-2"
              >
                <ChatBubbleLeftRightIcon className="w-4 h-4" />
                <span>Ask the AI Assistant</span>
              </button>
              <a
                href="https://buymeacoffee.com/rutgersbus"
                target="_blank"
                rel="noopener noreferrer"
                className="btn-ghost px-6 py-3 rounded-lg inline-flex items-center space-x-2"
              >
                <HeartIcon className="w-4 h-4" />
                <span>Support the Project</span>
              </a>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default BugReportPage;