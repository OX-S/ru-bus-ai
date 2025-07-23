import React from 'react';
import App from './src/App';

// Import all chat components for preview
import ChatContainer from './src/components/Chat/ChatContainer';
import ChatMessage from './src/components/Chat/ChatMessage';
import ChatInput from './src/components/Chat/ChatInput';
import LoadingSpinner from './src/components/Chat/LoadingSpinner';
import ErrorBubble from './src/components/Chat/ErrorBubble';

function RutgersBusApp() {
  return (
    <div>
      {/* Main App */}
      <App />
      
      {/* Hidden components for preview system */}
      <div style={{ display: 'none' }}>
        <ChatContainer />
        <ChatMessage message="Test message" isUser={true} timestamp={new Date().toISOString()} />
        <ChatInput onSendMessage={() => {}} />
        <LoadingSpinner />
        <ErrorBubble />
      </div>
    </div>
  );
}

export default RutgersBusApp;