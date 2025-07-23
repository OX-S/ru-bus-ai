import React from 'react';
import { ChatBubbleLeftRightIcon, ClockIcon, MapPinIcon } from '@heroicons/react/24/outline';
import FeatureCard from './FeatureCard';
import StatsCard from './StatsCard';

function FeaturesSection() {
  const features = [
    {
      icon: ChatBubbleLeftRightIcon,
      title: "Intelligent Conversations",
      description: "Ask complex questions in natural language and get precise, contextual answers about routes, schedules, and campus navigation.",
      gradientFrom: "red-500",
      gradientTo: "red-600",
      animationDelay: "0s"
    },
    {
      icon: ClockIcon,
      title: "Real-time Intelligence",
      description: "Access live bus tracking, delay notifications, and dynamic route suggestions powered by real-time campus data.",
      gradientFrom: "amber-500",
      gradientTo: "orange-600",
      animationDelay: "1s"
    },
    {
      icon: MapPinIcon,
      title: "Complete Coverage",
      description: "Comprehensive knowledge of all Rutgers campuses, routes, stops, and connections for seamless navigation.",
      gradientFrom: "emerald-500",
      gradientTo: "teal-600",
      animationDelay: "2s"
    }
  ];

  const stats = [
    { value: "24/7", label: "Always Available" },
    { value: "5+", label: "Campus Routes" },
    { value: "100+", label: "Bus Stops" },
    { value: "1000+", label: "Happy Students" }
  ];

  return (
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
          {features.map((feature, index) => (
            <FeatureCard key={index} {...feature} />
          ))}
        </div>

        {/* Stats Section */}
        <StatsCard stats={stats} />
      </div>
    </section>
  );
}

export default FeaturesSection;