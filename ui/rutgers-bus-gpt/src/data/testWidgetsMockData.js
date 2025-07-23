// Mock data for widget testing

// Example configurations for testing
export const mockExampleConfigs = [
  {
    type: "chat_message",
    message: "Hello! I can help you with bus routes and directions around Rutgers campus."
  },
  {
    type: "active_routes",
    routes: [
      {
        id: "route-a",
        name: "Route A",
        color: "red",
        stops: [
          "College Ave Student Center",
          "Scott Hall",
          "Academic Building",
          "Livingston Student Center",
          "Livingston Plaza"
        ]
      },
      {
        id: "route-b",
        name: "Route B",
        color: "blue",
        stops: [
          "Busch Student Center",
          "Hill Center",
          "Library of Science",
          "Stadium",
          "Werblin Recreation Center"
        ]
      },
      {
        id: "route-h",
        name: "Route H",
        color: "green",
        stops: [
          "College Ave Student Center",
          "George Street",
          "Robert Wood Johnson Hospital",
          "Medical School"
        ]
      }
    ]
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
    stopName: "College Ave Student Center",
    arrivals: [
      {
        route: "Route A",
        color: "red",
        destination: "Livingston Plaza",
        arrivalMinutes: 0
      },
      {
        route: "Route H",
        color: "green",
        destination: "Medical School",
        arrivalMinutes: 3
      },
      {
        route: "Route B",
        color: "blue",
        destination: "Busch Campus",
        arrivalMinutes: 8
      },
      {
        route: "Route A",
        color: "red",
        destination: "Livingston Plaza",
        arrivalMinutes: 12
      }
    ]
  },
  {
    type: "bus_arrivals",
    stopName: "Library of Science",
    arrivals: []
  }
];

// Data for testing widget rendering
export const mockRootProps = {
  isDevelopment: true,
  currentConfig: null,
  renderError: null
};