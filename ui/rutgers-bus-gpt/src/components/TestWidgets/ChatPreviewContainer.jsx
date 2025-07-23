import React, { useState, useRef, useEffect } from 'react';
import ChatMessage from '../Chat/ChatMessage';
import ChatInput from '../Chat/ChatInput';
import LoadingSpinner from '../Chat/LoadingSpinner';
import ErrorBubble from '../Chat/ErrorBubble';
import { WidgetType } from '../../utils/enums';
import ActiveRoutesWidget from './ActiveRoutesWidget';
import DirectionsWidget from './DirectionsWidget';
import BusArrivalsWidget from './BusArrivalsWidget';

function ChatPreviewContainer({ config, renderError }) {
  const [messages, setMessages] = useState([
    {
      id: 1,
      message: "Hello! I'm your Rutgers Bus Navigator. Ask me anything about bus routes, schedules, or campus navigation!",
      isUser: false,
      timestamp: new Date().toISOString()
    }
  ]);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, config, renderError]);

  // Add widget or chat message when config changes
  useEffect(() => {
    if (config) {
      // Add a user message asking for the widget
      const userMessage = {
        id: Date.now(),
        message: getMessageForConfig(config),
        isUser: true,
        timestamp: new Date().toISOString()
      };

      // Add the widget response
      const widgetMessage = {
        id: Date.now() + 1,
        config: config,
        isUser: false,
        isWidget: config.type !== WidgetType.CHAT_MESSAGE,
        message: config.type === WidgetType.CHAT_MESSAGE ? config.message : null,
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, userMessage, widgetMessage]);
    }
  }, [config]);

  const getMessageForConfig = (config) => {
    switch (config.type) {
      case WidgetType.CHAT_MESSAGE:
        return "Show me a chat message";
      case WidgetType.ACTIVE_ROUTES:
        return "What are the current active routes?";
      case WidgetType.DIRECTIONS:
        return `How do I get from ${config.from} to ${config.to}?`;
      case WidgetType.BUS_ARRIVALS:
        return `When are the next buses arriving at ${config.stopName}?`;
      default:
        return "Show me this widget";
    }
  };

  const handleSendMessage = (messageText) => {
    const userMessage = {
      id: Date.now(),
      message: messageText,
      isUser: true,
      timestamp: new Date().toISOString()
    };

    const responseMessage = {
      id: Date.now() + 1,
      message: "This is a preview environment. Use the configuration input to test widgets.",
      isUser: false,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage, responseMessage]);
  };

  const clearMessages = () => {
    setMessages([
      {
        id: 1,
        message: "Hello! I'm your Rutgers Bus Navigator. Ask me anything about bus routes, schedules, or campus navigation!",
        isUser: false,
        timestamp: new Date().toISOString()
      }
    ]);
  };

  const renderMessage = (msg) => {
    if (msg.isWidget && msg.config) {
      return (
        <div key={msg.id} className="mb-6">
          <div className="flex items-start space-x-3">
            <div className="p-2 rounded-xl shadow-md bg-gradient-to-br from-gray-100 to-gray-200">
              <div className="w-5 h-5 rounded-full bg-red-500"></div>
            </div>
            <div className="flex-1 max-w-xs sm:max-w-md md:max-w-lg">
              <div className="inline-block rounded-2xl shadow-sm bg-white border border-gray-200 overflow-hidden">
                {msg.config.type === WidgetType.ACTIVE_ROUTES && (
                  <div className="p-3">
                    <ActiveRoutesWidget routes={msg.config.routes} />
                  </div>
                )}
                {msg.config.type === WidgetType.DIRECTIONS && (
                  <div className="p-3">
                    <DirectionsWidget
                      from={msg.config.from}
                      to={msg.config.to}
                      directions={msg.config.directions}
                      totalTime={msg.config.totalTime}
                      walkingTime={msg.config.walkingTime}
                    />
                  </div>
                )}
                {msg.config.type === WidgetType.BUS_ARRIVALS && (
                  <div className="p-3">
                    <BusArrivalsWidget
                      stopName={msg.config.stopName}
                      arrivals={msg.config.arrivals}
                    />
                  </div>
                )}
              </div>
              <p className="text-xs text-gray-500 mt-1 font-body">
                {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </p>
            </div>
          </div>
        </div>
      );
    }

    return (
      <ChatMessage
        key={msg.id}
        message={msg.message}
        isUser={msg.isUser}
        timestamp={msg.timestamp}
      />
    );
  };

  return (
    <div className="glass-card rounded-3xl p-6 md:p-8 max-w-4xl mx-auto h-[600px] flex flex-col">
      {/* Chat Header */}
      <div className="border-b border-gray-200 pb-4 mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="font-display text-xl font-bold text-gray-800">
              Chat Preview
            </h2>
            <p className="font-body text-sm text-gray-600 mt-1">
              See exactly how widgets will appear in the chat interface
            </p>
          </div>
          <button
            onClick={clearMessages}
            className="text-sm text-gray-500 hover:text-red-600 font-body px-3 py-1 rounded-lg hover:bg-red-50 transition-colors"
          >
            Clear Chat
          </button>
        </div>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto mb-6 pr-2" style={{
        scrollbarWidth: 'thin',
        scrollbarColor: 'var(--color-border) transparent'
      }}>
        {messages.map(renderMessage)}
        
        {renderError && (
          <ErrorBubble
            message={`Configuration Error: ${renderError}`}
          />
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Chat Input */}
      <div className="border-t border-gray-200 pt-4">
        <ChatInput
          onSendMessage={handleSendMessage}
          placeholder="Type a message to test the chat interface..."
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
              className="text-xs px-3 py-1 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-full font-body transition-colors"
            >
              {suggestion}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

export default ChatPreviewContainer;