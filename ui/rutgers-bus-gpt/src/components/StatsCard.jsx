import React from 'react';

function StatsCard({ stats }) {
  return (
    <div className="glass-card rounded-3xl p-8 md:p-12">
      <div className="grid md:grid-cols-4 gap-8 text-center">
        {stats.map((stat, index) => (
          <div key={index}>
            <div className="font-display text-3xl md:text-4xl font-bold text-gradient mb-2">
              {stat.value}
            </div>
            <p className="font-body text-gray-600">{stat.label}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default StatsCard;