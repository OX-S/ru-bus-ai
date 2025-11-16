export type ChatMessageConfig = {
  type: "chat_message";
  message: string;
};

export type BusArrivalsConfig = {
  type: "bus_arrivals";
  stopIds: string[];
};

export type ActiveRoutesConfig = {
  type: "active_routes";
};

export type LLMOutput = ChatMessageConfig | BusArrivalsConfig | ActiveRoutesConfig;

