import React from 'react';
import Navigation from '../components/Navigation';
import HeroSection from '../components/HeroSection';
import FeaturesSection from '../components/FeaturesSection';
import CTASection from '../components/CTASection';
import Footer from '../components/Footer';

function HomePage({ navigate }) {
  return (
    <div className="min-h-screen">
      <Navigation navigate={navigate} />
      <HeroSection navigate={navigate} />
      <FeaturesSection />
      <CTASection navigate={navigate} />
      <Footer navigate={navigate} />
    </div>
  );
}

export default HomePage;