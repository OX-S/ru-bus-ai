import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import TestWidgetsPage from './src/pages/TestWidgetsPage';
import ActiveRoutesWidget from './src/components/TestWidgets/ActiveRoutesWidget';
import DirectionsWidget from './src/components/TestWidgets/DirectionsWidget';
import WidgetRenderer from './src/components/TestWidgets/WidgetRenderer';
import ConfigInputSection from './src/components/TestWidgets/ConfigInputSection';
import ExampleConfigsSection from './src/components/TestWidgets/ExampleConfigsSection';
import RouteItem from './src/components/TestWidgets/RouteItem';
import DirectionStep from './src/components/TestWidgets/DirectionStep';
import ExampleConfigCard from './src/components/TestWidgets/ExampleConfigCard';

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen" style={{ backgroundColor: 'var(--color-background)' }}>
        <TestWidgetsPage />
      </div>
    </BrowserRouter>
  );
}

export default App;