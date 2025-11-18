"use client";

import { useEffect, useRef, useState } from "react";
import type { AgentEvent, EventType } from "@/types/events";

type EventHandlerMap = {
  [eventType in EventType]?: (event: AgentEvent) => void;
} & {
  [eventType: string]: (event: AgentEvent) => void;
};

export function useAgentEvents(
  sessionId: string | null,
  handlers: EventHandlerMap = {},
  onEvent?: (event: AgentEvent) => void
) {
  const eventSourceRef = useRef<EventSource | null>(null);
  const [connected, setConnected] = useState(false);
  const reconnectTimer = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (!sessionId) return;

    let retryCount = 0;

    const connect = () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }

      const es = new EventSource(`/api/events/${sessionId}`);
      eventSourceRef.current = es;

      es.onopen = () => {
        setConnected(true);
        retryCount = 0;
        console.log(`[SSE] Connected to session: ${sessionId}`);
      };

      es.onerror = () => {
        setConnected(false);
        console.warn("[SSE] Connection lost. Retrying...");

        es.close();

        if (reconnectTimer.current) clearTimeout(reconnectTimer.current);

        reconnectTimer.current = setTimeout(() => {
          retryCount += 1;
          connect();
        }, Math.min(3000 * retryCount, 15000)); // exponential backoff max 15s
      };

      es.onmessage = (event) => {
        // fallback for unnamed events
        try {
          const parsed: AgentEvent = JSON.parse(event.data);

          if (onEvent) onEvent(parsed);
          const handler = handlers[parsed.type];
          if (handler) handler(parsed);
        } catch (err) {
          console.error("Error parsing SSE message:", err);
        }
      };

      // For named events (AG-UI types)
      for (const eventType of Object.keys(handlers)) {
        es.addEventListener(eventType, (rawEvent) => {
          const data = (rawEvent as MessageEvent).data;
          try {
            const parsed: AgentEvent = JSON.parse(data);
            handlers[eventType]?.(parsed);
            onEvent?.(parsed);
          } catch (err) {
            console.error("Failed to parse event:", err);
          }
        });
      }
    };

    connect();

    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
      if (reconnectTimer.current) {
        clearTimeout(reconnectTimer.current);
      }
    };
  }, [sessionId]);

  return { connected };
}
