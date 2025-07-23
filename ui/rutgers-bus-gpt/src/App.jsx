import React, { useState } from 'react';
import { 
  ChatBubbleLeftRightIcon, 
  BugAntIcon, 
  TruckIcon,
  HeartIcon,
  HomeIcon,
  ExclamationTriangleIcon,
  SparklesIcon,
  RocketLaunchIcon,
  ShieldCheckIcon,
  ClockIcon,
  MapPinIcon,
  ArrowRightIcon
} from '@heroicons/react/24/outline';

function App() {
  const [currentRoute, setCurrentRoute] = useState('/');

  const navigate = (path) => {
    setCurrentRoute(path);
    window.history.pushState({}, '', path);
  };

  // Handle browser back/forward buttons
  React.useEffect(() => {
    const handlePopState = () => {
      setCurrentRoute(window.location.pathname);
    };
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  const renderPage = () => {
    switch (currentRoute) {
      case '/':
        return <HomePage navigate={navigate} />;
      case '/chat':
        return <ChatPage navigate={navigate} />;
      case '/bug-reports':
        return <BugReportPage navigate={navigate} />;
      default:
        return <NotFoundPage navigate={navigate} />;
    }
  };

  return (
    <div className="min-h-screen" style={{ backgroundColor: 'var(--color-background)' }}>
      {renderPage()}
    </div>
  );
}

function HomePage({ navigate }) {
  return (
    <div className="min-h-screen">
      {/* Premium Navigation */}
      <nav className="nav-premium fixed w-full top-0 z-50 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="p-2 bg-gradient-to-br from-red-500 to-red-600 rounded-xl shadow-lg">
              <TruckIcon className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="font-display text-xl font-bold text-gradient">
                RU Bus AI
              </h1>
              <p className="text-xs text-gray-500 font-body">Smart Campus Transit</p>
            </div>
          </div>
          <div className="flex items-center space-x-6">
            <button
              onClick={() => navigate('/bug-reports')}
              className="btn-ghost flex items-center space-x-2 px-4 py-2 rounded-lg"
            >
              <BugAntIcon className="w-4 h-4" />
              <span className="font-body text-sm font-medium">Feedback</span>
            </button>
            <a
              href="https://buymeacoffee.com/rutgersbus"
              target="_blank"
              rel="noopener noreferrer"
              className="btn-ghost flex items-center space-x-2 px-4 py-2 rounded-lg"
            >
              <HeartIcon className="w-4 h-4" />
              <span className="font-body text-sm font-medium">Support</span>
            </a>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="hero-bg pt-24 pb-16 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center max-w-4xl mx-auto mb-16">
            {/* Hero Badge */}
            <div className="inline-flex items-center space-x-2 bg-white/80 backdrop-blur-sm border border-red-100 rounded-full px-4 py-2 mb-8 shadow-lg">
              <SparklesIcon className="w-4 h-4 text-red-500" />
              <span className="font-body text-sm font-medium text-gray-700">
                AI-Powered Campus Navigation
              </span>
            </div>

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
            <div className="flex flex-wrap items-center justify-center gap-8 text-sm text-gray-500 font-body">
              <div className="flex items-center space-x-2">
                <ShieldCheckIcon className="w-4 h-4" />
                <span>Secure & Private</span>
              </div>
              <div className="flex items-center space-x-2">
                <ClockIcon className="w-4 h-4" />
                <span>Real-time Updates</span>
              </div>
              <div className="flex items-center space-x-2">
                <MapPinIcon className="w-4 h-4" />
                <span>Campus-wide Coverage</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="font-display text-4xl md:text-5xl font-bold mb-6" style={{ color: 'var(--color-text-primary)' }}>
              Why Students Choose
              <span className="text-gradient block">RU Bus AI</span>
            </h2>
            <p className="text-xl text-gray-600 font-body max-w-2xl mx-auto">
              Cutting-edge AI technology meets practical campus navigation needs
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 mb-16">
            <div className="feature-card group">
              <div className="relative z-10">
                <div className="w-16 h-16 bg-gradient-to-br from-red-500 to-red-600 rounded-2xl flex items-center justify-center mb-6 animate-float shadow-lg">
                  <ChatBubbleLeftRightIcon className="w-8 h-8 text-white" />
                </div>
                <h3 className="font-display text-xl font-bold mb-4" style={{ color: 'var(--color-text-primary)' }}>
                  Intelligent Conversations
                </h3>
                <p className="font-body text-gray-600 leading-relaxed">
                  Ask complex questions in natural language and get precise, contextual answers about routes, schedules, and campus navigation.
                </p>
              </div>
            </div>

            <div className="feature-card group">
              <div className="relative z-10">
                <div className="w-16 h-16 bg-gradient-to-br from-amber-500 to-orange-600 rounded-2xl flex items-center justify-center mb-6 animate-float shadow-lg" style={{ animationDelay: '1s' }}>
                  <ClockIcon className="w-8 h-8 text-white" />
                </div>
                <h3 className="font-display text-xl font-bold mb-4" style={{ color: 'var(--color-text-primary)' }}>
                  Real-time Intelligence
                </h3>
                <p className="font-body text-gray-600 leading-relaxed">
                  Access live bus tracking, delay notifications, and dynamic route suggestions powered by real-time campus data.
                </p>
              </div>
            </div>

            <div className="feature-card group">
              <div className="relative z-10">
                <div className="w-16 h-16 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-2xl flex items-center justify-center mb-6 animate-float shadow-lg" style={{ animationDelay: '2s' }}>
                  <MapPinIcon className="w-8 h-8 text-white" />
                </div>
                <h3 className="font-display text-xl font-bold mb-4" style={{ color: 'var(--color-text-primary)' }}>
                  Complete Coverage
                </h3>
                <p className="font-body text-gray-600 leading-relaxed">
                  Comprehensive knowledge of all Rutgers campuses, routes, stops, and connections for seamless navigation.
                </p>
              </div>
            </div>
          </div>

          {/* Stats Section */}
          <div className="glass-card rounded-3xl p-8 md:p-12">
            <div className="grid md:grid-cols-4 gap-8 text-center">
              <div>
                <div className="font-display text-3xl md:text-4xl font-bold text-gradient mb-2">24/7</div>
                <p className="font-body text-gray-600">Always Available</p>
              </div>
              <div>
                <div className="font-display text-3xl md:text-4xl font-bold text-gradient mb-2">5+</div>
                <p className="font-body text-gray-600">Campus Routes</p>
              </div>
              <div>
                <div className="font-display text-3xl md:text-4xl font-bold text-gradient mb-2">100+</div>
                <p className="font-body text-gray-600">Bus Stops</p>
              </div>
              <div>
                <div className="font-display text-3xl md:text-4xl font-bold text-gradient mb-2">1000+</div>
                <p className="font-body text-gray-600">Happy Students</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
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

      {/* Premium Footer */}
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
    </div>
  );
}

function ChatPage({ navigate }) {
  return (
    <div className="min-h-screen">
      {/* Premium Navigation */}
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
              <h1 className="font-display text-xl font-bold text-gradient">RU Bus AI</h1>
              <p className="text-xs text-gray-500 font-body">Smart Campus Transit</p>
            </div>
          </button>
          <button
            onClick={() => navigate('/')}
            className="btn-ghost flex items-center space-x-2 px-4 py-2 rounded-lg"
          >
            <HomeIcon className="w-4 h-4" />
            <span className="font-body text-sm font-medium">Home</span>
          </button>
        </div>
      </nav>

      {/* Chat Interface */}
      <main className="pt-24 pb-16 px-6 min-h-screen hero-bg">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <div className="inline-flex items-center space-x-2 bg-white/80 backdrop-blur-sm border border-red-100 rounded-full px-4 py-2 mb-8 shadow-lg">
              <ChatBubbleLeftRightIcon className="w-4 h-4 text-red-500" />
              <span className="font-body text-sm font-medium text-gray-700">
                AI Chat Interface
              </span>
            </div>

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

function BugReportPage({ navigate }) {
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
      {/* Premium Navigation */}
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
              <h1 className="font-display text-xl font-bold text-gradient">RU Bus AI</h1>
              <p className="text-xs text-gray-500 font-body">Smart Campus Transit</p>
            </div>
          </button>
          <button
            onClick={() => navigate('/')}
            className="btn-ghost flex items-center space-x-2 px-4 py-2 rounded-lg"
          >
            <HomeIcon className="w-4 h-4" />
            <span className="font-body text-sm font-medium">Home</span>
          </button>
        </div>
      </nav>

      {/* Bug Report Form */}
      <main className="pt-24 pb-16 px-6 min-h-screen hero-bg">
        <div className="max-w-3xl mx-auto">
          <div className="text-center mb-12">
            <div className="inline-flex items-center space-x-2 bg-white/80 backdrop-blur-sm border border-red-100 rounded-full px-4 py-2 mb-8 shadow-lg">
              <BugAntIcon className="w-4 h-4 text-red-500" />
              <span className="font-body text-sm font-medium text-gray-700">
                Feedback & Bug Reports
              </span>
            </div>

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

function NotFoundPage({ navigate }) {
  return (
    <div className="min-h-screen">
      {/* Premium Navigation */}
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
              <h1 className="font-display text-xl font-bold text-gradient">RU Bus AI</h1>
              <p className="text-xs text-gray-500 font-body">Smart Campus Transit</p>
            </div>
          </button>
        </div>
      </nav>

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

export default App;