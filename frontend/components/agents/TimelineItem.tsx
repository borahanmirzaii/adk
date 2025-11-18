"use client";

import { EventIcon } from "./EventIcon";
import { ToolCallCard } from "./ToolCallCard";
import { WorkflowStepBadge } from "./WorkflowStepBadge";
import type { AgentEvent } from "@/types/events";
import { cn } from "@/lib/utils";
import { motion } from "framer-motion";

interface TimelineItemProps {
  event: AgentEvent;
  isLast?: boolean;
}

export function TimelineItem({ event, isLast }: TimelineItemProps) {
  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  const renderEventContent = () => {
    switch (event.type) {
      case "tool_call_started":
      case "tool_call_result": {
        const payload = event.payload as any;
        return (
          <ToolCallCard
            toolName={payload.tool_name}
            args={payload.args || {}}
            result={event.type === "tool_call_result" ? payload.result : undefined}
            error={event.type === "tool_call_result" ? payload.error : undefined}
            timestamp={event.timestamp}
          />
        );
      }
      case "workflow_step_started":
      case "workflow_step_completed": {
        const payload = event.payload as any;
        return (
          <WorkflowStepBadge
            stepId={payload.step_id}
            status={
              event.type === "workflow_step_completed"
                ? "completed"
                : "active"
            }
          />
        );
      }
      case "agent_message_delta":
      case "agent_message_end": {
        const payload = event.payload as any;
        return (
          <div className="text-sm text-gray-700 dark:text-gray-300">
            {payload.delta || payload.content}
          </div>
        );
      }
      case "agent_thought": {
        const payload = event.payload as any;
        return (
          <div className="text-sm italic text-gray-600 dark:text-gray-400">
            {payload.content}
          </div>
        );
      }
      case "run_error": {
        const payload = event.payload as any;
        return (
          <div className="text-sm text-red-700 dark:text-red-400">
            {payload.message}
          </div>
        );
      }
      default:
        return (
          <div className="text-xs text-gray-500 dark:text-gray-500">
            {JSON.stringify(event.payload, null, 2)}
          </div>
        );
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className="relative flex gap-4"
    >
      {/* Timeline line */}
      {!isLast && (
        <div className="absolute left-3 top-8 bottom-0 w-0.5 bg-gray-200 dark:bg-gray-700" />
      )}

      {/* Icon */}
      <div className="relative z-10 flex-shrink-0">
        <div className="w-6 h-6 rounded-full bg-white dark:bg-gray-800 border-2 border-gray-300 dark:border-gray-600 flex items-center justify-center">
          <EventIcon type={event.type} />
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0 pb-6">
        <div className="flex items-center gap-2 mb-2">
          <span className="text-xs font-medium text-gray-900 dark:text-gray-100">
            {event.type}
          </span>
          <span className="text-xs text-gray-500">{formatTime(event.timestamp)}</span>
        </div>
        <div className="mt-2">{renderEventContent()}</div>
      </div>
    </motion.div>
  );
}

