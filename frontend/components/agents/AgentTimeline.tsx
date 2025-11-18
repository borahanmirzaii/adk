"use client";

import { useState, useMemo } from "react";
import { useAgentEvents } from "@/hooks/useAgentEvents";
import { TimelineItem } from "./TimelineItem";
import { CardSection } from "@/components/shared/CardSection";
import { LoadingState } from "@/components/shared/LoadingState";
import { ErrorState } from "@/components/shared/ErrorState";
import type { AgentEvent, EventType } from "@/types/events";
import { Filter } from "lucide-react";
import { MAX_EVENTS } from "@/lib/constants";

interface AgentTimelineProps {
  sessionId: string;
}

export function AgentTimeline({ sessionId }: AgentTimelineProps) {
  const [events, setEvents] = useState<AgentEvent[]>([]);
  const [filter, setFilter] = useState<EventType[] | null>(null);

  const { connected } =   useAgentEvents(
    sessionId,
    {
      session_started: (event) => {
        setEvents((prev) => {
          const updated = [...prev, event];
          return updated.slice(-MAX_EVENTS);
        });
      },
      session_ended: (event) => {
        setEvents((prev) => {
          const updated = [...prev, event];
          return updated.slice(-MAX_EVENTS);
        });
      },
      agent_message_start: (event) => {
        setEvents((prev) => {
          const updated = [...prev, event];
          return updated.slice(-MAX_EVENTS);
        });
      },
      agent_message_delta: (event) => {
        setEvents((prev) => {
          const lastIndex = prev.length - 1;
          const lastEvent = prev[lastIndex];
          if (
            lastEvent?.type === "agent_message_delta" &&
            lastEvent.payload.message_id === event.payload.message_id
          ) {
            // Merge delta into existing message
            const updated = [...prev];
            updated[lastIndex] = {
              ...lastEvent,
              payload: {
                ...lastEvent.payload,
                delta: (lastEvent.payload.delta || "") + event.payload.delta,
              },
            };
            return updated.slice(-MAX_EVENTS);
          }
          const updated = [...prev, event];
          return updated.slice(-MAX_EVENTS);
        });
      },
      agent_message_end: (event) => {
        setEvents((prev) => {
          const updated = [...prev, event];
          return updated.slice(-MAX_EVENTS);
        });
      },
      tool_call_started: (event) => {
        setEvents((prev) => {
          const updated = [...prev, event];
          return updated.slice(-MAX_EVENTS);
        });
      },
      tool_call_delta: (event) => {
        setEvents((prev) => {
          const updated = [...prev, event];
          return updated.slice(-MAX_EVENTS);
        });
      },
      tool_call_result: (event) => {
        setEvents((prev) => {
          const updated = [...prev, event];
          return updated.slice(-MAX_EVENTS);
        });
      },
      workflow_started: (event) => {
        setEvents((prev) => {
          const updated = [...prev, event];
          return updated.slice(-MAX_EVENTS);
        });
      },
      workflow_step_started: (event) => {
        setEvents((prev) => {
          const updated = [...prev, event];
          return updated.slice(-MAX_EVENTS);
        });
      },
      workflow_step_completed: (event) => {
        setEvents((prev) => {
          const updated = [...prev, event];
          return updated.slice(-MAX_EVENTS);
        });
      },
      workflow_transition: (event) => {
        setEvents((prev) => {
          const updated = [...prev, event];
          return updated.slice(-MAX_EVENTS);
        });
      },
      workflow_completed: (event) => {
        setEvents((prev) => {
          const updated = [...prev, event];
          return updated.slice(-MAX_EVENTS);
        });
      },
      agent_thought: (event) => {
        setEvents((prev) => {
          const updated = [...prev, event];
          return updated.slice(-MAX_EVENTS);
        });
      },
      run_error: (event) => {
        setEvents((prev) => {
          const updated = [...prev, event];
          return updated.slice(-MAX_EVENTS);
        });
      },
      run_retry: (event) => {
        setEvents((prev) => {
          const updated = [...prev, event];
          return updated.slice(-MAX_EVENTS);
        });
      },
      run_interrupted: (event) => {
        setEvents((prev) => {
          const updated = [...prev, event];
          return updated.slice(-MAX_EVENTS);
        });
      },
      retrieval_started: (event) => {
        setEvents((prev) => {
          const updated = [...prev, event];
          return updated.slice(-MAX_EVENTS);
        });
      },
      retrieval_result: (event) => {
        setEvents((prev) => {
          const updated = [...prev, event];
          return updated.slice(-MAX_EVENTS);
        });
      },
      automation_triggered: (event) => {
        setEvents((prev) => {
          const updated = [...prev, event];
          return updated.slice(-MAX_EVENTS);
        });
      },
      automation_completed: (event) => {
        setEvents((prev) => {
          const updated = [...prev, event];
          return updated.slice(-MAX_EVENTS);
        });
      },
      metrics_update: (event) => {
        setEvents((prev) => {
          const updated = [...prev, event];
          return updated.slice(-MAX_EVENTS);
        });
      },
    },
    (event) => {
      // Global event handler
    }
  );

  const filteredEvents = useMemo(() => {
    if (!filter || filter.length === 0) return events;
    return events.filter((event) => filter.includes(event.type));
  }, [events, filter]);

  // Virtualization setup
  const parentRef = useRef<HTMLDivElement>(null);
  const virtualizer = useVirtualizer({
    count: filteredEvents.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 100, // Estimated height per item
    overscan: 5, // Render 5 extra items outside viewport
  });

  if (!connected && events.length === 0) {
    return (
      <CardSection title="Agent Timeline">
        <LoadingState message="Connecting to event stream..." />
      </CardSection>
    );
  }

  return (
    <CardSection
      title="Agent Timeline"
      headerActions={
        <button
          onClick={() => setFilter(null)}
          className="text-xs text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100"
        >
          <Filter className="w-4 h-4" />
        </button>
      }
      className="h-full flex flex-col"
    >
      <div
        ref={parentRef}
        className="flex-1 overflow-auto"
        style={{ contain: "strict" }}
      >
        {filteredEvents.length === 0 ? (
          <div className="text-center py-8 text-sm text-gray-500">
            No events yet
          </div>
        ) : (
          <div
            style={{
              height: `${virtualizer.getTotalSize()}px`,
              width: "100%",
              position: "relative",
            }}
          >
            {virtualizer.getVirtualItems().map((virtualItem) => {
              const event = filteredEvents[virtualItem.index];
              return (
                <div
                  key={virtualItem.key}
                  style={{
                    position: "absolute",
                    top: 0,
                    left: 0,
                    width: "100%",
                    height: `${virtualItem.size}px`,
                    transform: `translateY(${virtualItem.start}px)`,
                  }}
                >
                  <TimelineItem
                    event={event}
                    isLast={virtualItem.index === filteredEvents.length - 1}
                  />
                </div>
              );
            })}
          </div>
        )}
      </div>
    </CardSection>
  );
}

