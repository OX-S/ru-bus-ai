// Mock data for widget testing

// Example configurations for testing
export const mockExampleConfigs = [
  {
    type: "chat_message",
    message: "Hello! I can help you with bus routes and directions around Rutgers campus."
  },
  {
    type: "active_routes",
  },
  {
    type: "directions",
    from: "College Ave Student Center",
    to: "Busch Student Center",
    directions: [
      {
        step: 1,
        action: "Take",
        route: "Route A",
        color: "red",
        from: "College Ave Student Center",
        to: "Livingston Student Center"
      },
      {
        step: 2,
        action: "Transfer at",
        location: "Livingston Student Center",
        waitTime: 5
      },
      {
        step: 3,
        action: "Take",
        route: "Route B",
        color: "blue",
        from: "Livingston Student Center",
        to: "Busch Student Center"
      }
    ],
    totalTime: 25,
    walkingTime: 3
  },
  {
    type: "bus_arrivals",
    stopIds: ["27767"]
  },
  {
    type: "bus_arrivals",
    stopIds: ["27767", "27768"]
  }
];

// Data for testing widget rendering
export const mockRootProps = {
  isDevelopment: true,
  currentConfig: null,
  renderError: null
};