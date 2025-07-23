import React from 'react';

function FeatureCard({ icon: Icon, title, description, gradientFrom, gradientTo, animationDelay = '0s' }) {
  return (
    <div className="feature-card group">
      <div className="relative z-10">
        <div 
          className={`w-16 h-16 bg-gradient-to-br from-${gradientFrom} to-${gradientTo} rounded-2xl flex items-center justify-center mb-6 animate-float shadow-lg`}
          style={{ animationDelay }}
        >
          <Icon className="w-8 h-8 text-white" />
        </div>
        <h3 className="font-display text-xl font-bold mb-4" style={{ color: 'var(--color-text-primary)' }}>
          {title}
        </h3>
        <p className="font-body text-gray-600 leading-relaxed">
          {description}
        </p>
      </div>
    </div>
  );
}

export default FeatureCard;