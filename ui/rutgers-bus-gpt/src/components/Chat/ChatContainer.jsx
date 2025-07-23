import React, { useState, useRef, useEffect } from 'react';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import LoadingSpinner from './LoadingSpinner';
import ErrorBubble from './ErrorBubble';

function ChatContainer() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      message: "Hello! I'm your Rutgers Bus Navigator. Ask me anything about bus routes, schedules, or campus navigation!",
      isUser: false,
      timestamp: new Date().toISOString()
    }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading, error]);

  const sendMessageToAPI = async (message) => {
    try {
      const response = await fetch('http://localhost:3000/test', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data.response || "I received your message but couldn't generate a proper response.";
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  };

  const handleSendMessage = async (messageText) => {
    if (isLoading) return;

    // Add user message
    const userMessage = {
      id: Date.now(),
      message: messageText,
      isUser: true,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      // Add temporary delay to see loading state (remove this once endpoint is working)
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const response = await sendMessageToAPI(messageText);
      
      // Add AI response
      const aiMessage = {
        id: Date.now() + 1,
        message: response,
        isUser: false,
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      setError({
        id: Date.now() + 1,
        message: "Trouble generating response",
        onRetry: () => handleRetry(messageText)
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleRetry = (originalMessage) => {
    setError(null);
    handleSendMessage(originalMessage);
  };

  const clearError = () => {
    setError(null);
  };

  return (
    <div className="glass-card rounded-3xl p-6 md:p-8 max-w-4xl mx-auto h-[600px] flex flex-col">
      {/* Chat Header */}
      <div className="border-b border-gray-200 pb-4 mb-6">
        <h2 className="font-display text-xl font-bold text-gray-800">
          Rutgers Bus Navigator
        </h2>
        <p className="font-body text-sm text-gray-600 mt-1">
          Ask me about bus routes, schedules, and campus navigation
        </p>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto mb-6 pr-2" style={{
        scrollbarWidth: 'thin',
        scrollbarColor: 'var(--color-border) transparent'
      }}>
        {messages.map((msg) => (
          <ChatMessage
            key={msg.id}
            message={msg.message}
            isUser={msg.isUser}
            timestamp={msg.timestamp}
          />
        ))}
        
        {isLoading && <LoadingSpinner message="Generating response..." />}
        
        {error && (
          <ErrorBubble
            message={error.message}
            onRetry={error.onRetry}
          />
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Chat Input */}
      <div className="border-t border-gray-200 pt-4">
        <ChatInput
          onSendMessage={handleSendMessage}
          disabled={isLoading}
          placeholder="Ask me about Rutgers bus routes, schedules, or navigation..."
        />
        
        {/* Quick Actions */}
        <div className="flex flex-wrap gap-2 mt-3">
          {[
            "What buses go to College Ave?",
            "Show me the schedule for Route A",
            "How do I get to Busch Campus?",
            "Are there any delays today?"
          ].map((suggestion, index) => (
            <button
              key={index}
              onClick={() => handleSendMessage(suggestion)}
              disabled={isLoading}
              className="text-xs px-3 py-1 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-full font-body transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {suggestion}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

export default ChatContainer;