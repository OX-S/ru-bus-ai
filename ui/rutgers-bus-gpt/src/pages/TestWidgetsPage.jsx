import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { BeakerIcon } from '@heroicons/react/24/outline';
import Navigation from '../components/Navigation';
import HeroBadge from '../components/HeroBadge';
import ConfigInputSection from '../components/TestWidgets/ConfigInputSection';
import WidgetRenderer from '../components/TestWidgets/WidgetRenderer';
import ExampleConfigsSection from '../components/TestWidgets/ExampleConfigsSection';

function TestWidgetsPage() {
  const navigate = useNavigate();
  const [currentConfig, setCurrentConfig] = useState(null);
  const [renderError, setRenderError] = useState('');

  // Check if running in development mode
  if (!import.meta.env.DEV) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-800 mb-4">
            Page Not Available
          </h1>
          <p className="text-gray-600 mb-6">
            This page is only available in development mode.
          </p>
          <button
            onClick={() => navigate('/')}
            className="btn-primary font-body px-6 py-3 rounded-xl"
          >
            Go to Home
          </button>
        </div>
      </div>
    );
  }

  const handleConfigSubmit = (config) => {
    setRenderError('');
    setCurrentConfig(config);
  };

  const handleConfigSelect = (configString) => {
    try {
      const parsed = JSON.parse(configString);
      setCurrentConfig(parsed);
      setRenderError('');
    } catch (err) {
      setRenderError('Failed to parse selected configuration');
    }
  };

  const handleClear = () => {
    setCurrentConfig(null);
    setRenderError('');
  };

  const handleRenderError = (error) => {
    setRenderError(error);
  };

  return (
    <div className="min-h-screen">
      <Navigation navigate={navigate} showHomeButton={true} showFeedbackButton={false} showSupportButton={false} />

      <main className="pt-24 pb-16 px-6 min-h-screen hero-bg">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12">
            <HeroBadge 
              icon={BeakerIcon}
              text="Development Environment"
            />

            <h1 className="font-display text-4xl md:text-5xl font-bold mb-6" style={{ color: 'var(--color-text-primary)' }}>
              Test
              <span className="text-gradient block">Widgets</span>
            </h1>
            <p className="text-xl text-gray-600 font-body max-w-3xl mx-auto mb-12">
              This page is only available in development mode for testing widgets independently. 
              Enter JSON configurations to preview how widgets will render in the chat interface.
            </p>
          </div>

          {/* Main Content */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
            {/* Left Column - Configuration Input */}
            <div className="space-y-8">
              <ConfigInputSection 
                onConfigSubmit={handleConfigSubmit}
                onClear={handleClear}
              />
              
              <ExampleConfigsSection 
                onConfigSelect={handleConfigSelect}
              />
            </div>

            {/* Right Column - Chat Preview */}
            <div className="space-y-6">
              <WidgetRenderer 
                config={currentConfig}
                onError={handleRenderError}
                renderError={renderError}
              />
            </div>
          </div>

          {/* Navigation */}
          <div className="flex justify-center">
            <button
              onClick={() => navigate('/chat')}
              className="btn-primary font-body px-8 py-3 rounded-xl"
            >
              Back to Chat
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}

export default TestWidgetsPage;