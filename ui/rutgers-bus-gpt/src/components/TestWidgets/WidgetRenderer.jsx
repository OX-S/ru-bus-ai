import React from 'react';
import ChatPreviewContainer from './ChatPreviewContainer';

function WidgetRenderer({ config, onError, renderError }) {
  return (
    <ChatPreviewContainer 
      config={config}
      renderError={renderError}
    />
  );
}

export default WidgetRenderer;