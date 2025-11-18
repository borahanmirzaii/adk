"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import type { AgentEvent, EventType } from "@/types/events";
import toast from "react-hot-toast";

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
  const connectedRef = useRef(false);
  
  // Store handlers and onEvent in refs to avoid re-creating connections
  const handlersRef = useRef(handlers);
  const onEventRef = useRef(onEvent);
  
  // Update refs when handlers or onEvent change
  useEffect(() => {
    handlersRef.current = handlers;
  }, [handlers]);
  
  useEffect(() => {
    onEventRef.current = onEvent;
  }, [onEvent]);

  useEffect(() => {
    if (!sessionId) {
      // Clean up if sessionId becomes null
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
      setConnected(false);
      return;
    }

    let retryCount = 0;
    let isMounted = true;

    const connect = () => {
      if (!isMounted) return;
      
      // Close existing connection if any
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }

      const es = new EventSource(`/api/events/${sessionId}`);
      eventSourceRef.current = es;

      es.onopen = () => {
        connectedRef.current = true;
        setConnected(true);
        retryCount = 0;
        console.log(`[SSE] Connected to session: ${sessionId}`);
        toast.success("Connected to event stream", { id: `sse-${sessionId}` });
      };

      es.onerror = () => {
        const wasConnected = connectedRef.current;
        connectedRef.current = false;
        setConnected(false);
        
        if (wasConnected) {
          toast.error("Connection lost. Reconnecting...", { id: `sse-${sessionId}` });
        }
        
        console.warn("[SSE] Connection lost. Retrying...");

        es.close();

        if (reconnectTimer.current) clearTimeout(reconnectTimer.current);

        reconnectTimer.current = setTimeout(() => {
          retryCount += 1;
          if (isMounted) {
            connect();
          }
        }, Math.min(3000 * retryCount, 15000)); // exponential backoff max 15s
      };

      es.onmessage = (event) => {
        // fallback for unnamed events
        if (!isMounted) return;
        
        try {
          const parsed: AgentEvent = JSON.parse(event.data);

          // Use refs to get latest handlers/onEvent
          if (onEventRef.current) {
            onEventRef.current(parsed);
          }
          const handler = handlersRef.current[parsed.type];
          if (handler) {
            handler(parsed);
          }
        } catch (err) {
          console.error("Error parsing SSE message:", err);
          toast.error("Failed to parse event", { id: `parse-error-${Date.now()}` });
        }
      };

      // For named events (AG-UI types)
      for (const eventType of Object.keys(handlersRef.current)) {
        es.addEventListener(eventType, (rawEvent) => {
          if (!isMounted) return;
          
          const data = (rawEvent as MessageEvent).data;
          try {
            const parsed: AgentEvent = JSON.parse(data);
            handlersRef.current[eventType]?.(parsed);
            onEventRef.current?.(parsed);
          } catch (err) {
            console.error("Failed to parse event:", err);
            toast.error("Failed to parse event", { id: `parse-error-${Date.now()}` });
          }
        });
      }
    };

    connect();

    return () => {
      isMounted = false;
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
      if (reconnectTimer.current) {
        clearTimeout(reconnectTimer.current);
        reconnectTimer.current = null;
      }
    };
  }, [sessionId]); // Only depend on sessionId, handlers/onEvent accessed via refs

  return { connected };
}
