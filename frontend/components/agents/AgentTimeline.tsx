"use client";

import { useState, useMemo } from "react";
import { useAgentEvents } from "@/hooks/useAgentEvents";
import { TimelineItem } from "./TimelineItem";
import { CardSection } from "@/components/shared/CardSection";
import { LoadingState } from "@/components/shared/LoadingState";
import { ErrorState } from "@/components/shared/ErrorState";
import type { AgentEvent, EventType } from "@/types/events";
import { Filter } from "lucide-react";

interface AgentTimelineProps {
  sessionId: string;
}

export function AgentTimeline({ sessionId }: AgentTimelineProps) {
  const [events, setEvents] = useState<AgentEvent[]>([]);
  const [filter, setFilter] = useState<EventType[] | null>(null);

  const { connected } = useAgentEvents(
    sessionId,
    {
      session_started: (event) => {
        setEvents((prev) => [...prev, event]);
      },
      session_ended: (event) => {
        setEvents((prev) => [...prev, event]);
      },
      agent_message_start: (event) => {
        setEvents((prev) => [...prev, event]);
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
            return updated;
          }
          return [...prev, event];
        });
      },
      agent_message_end: (event) => {
        setEvents((prev) => [...prev, event]);
      },
      tool_call_started: (event) => {
        setEvents((prev) => [...prev, event]);
      },
      tool_call_delta: (event) => {
        setEvents((prev) => [...prev, event]);
      },
      tool_call_result: (event) => {
        setEvents((prev) => [...prev, event]);
      },
      workflow_started: (event) => {
        setEvents((prev) => [...prev, event]);
      },
      workflow_step_started: (event) => {
        setEvents((prev) => [...prev, event]);
      },
      workflow_step_completed: (event) => {
        setEvents((prev) => [...prev, event]);
      },
      workflow_transition: (event) => {
        setEvents((prev) => [...prev, event]);
      },
      workflow_completed: (event) => {
        setEvents((prev) => [...prev, event]);
      },
      agent_thought: (event) => {
        setEvents((prev) => [...prev, event]);
      },
      run_error: (event) => {
        setEvents((prev) => [...prev, event]);
      },
      run_retry: (event) => {
        setEvents((prev) => [...prev, event]);
      },
      run_interrupted: (event) => {
        setEvents((prev) => [...prev, event]);
      },
      retrieval_started: (event) => {
        setEvents((prev) => [...prev, event]);
      },
      retrieval_result: (event) => {
        setEvents((prev) => [...prev, event]);
      },
      automation_triggered: (event) => {
        setEvents((prev) => [...prev, event]);
      },
      automation_completed: (event) => {
        setEvents((prev) => [...prev, event]);
      },
      metrics_update: (event) => {
        setEvents((prev) => [...prev, event]);
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
    >
      <div className="space-y-0">
        {filteredEvents.length === 0 ? (
          <div className="text-center py-8 text-sm text-gray-500">
            No events yet
          </div>
        ) : (
          filteredEvents.map((event, index) => (
            <TimelineItem
              key={event.event_id}
              event={event}
              isLast={index === filteredEvents.length - 1}
            />
          ))
        )}
      </div>
    </CardSection>
  );
}

