"use client";

import { EventIcon } from "./EventIcon";
import { ToolCallCard } from "./ToolCallCard";
import { WorkflowStepBadge } from "./WorkflowStepBadge";
import type { AgentEvent } from "@/types/events";
import { cn } from "@/lib/utils";
import { motion } from "framer-motion";
import {
  isToolCallStartedPayload,
  isToolCallResultPayload,
  isWorkflowStepStartedPayload,
  isWorkflowStepCompletedPayload,
  isAgentMessageDeltaPayload,
  isAgentMessageEndPayload,
  isAgentThoughtPayload,
  isRunErrorPayload,
} from "@/lib/typeGuards";
import { sanitizeJson, escapeHtml } from "@/lib/sanitize";

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
      case "tool_call_started": {
        if (isToolCallStartedPayload(event.payload)) {
          return (
            <ToolCallCard
              toolName={event.payload.tool_name}
              args={event.payload.args || {}}
              timestamp={event.timestamp}
            />
          );
        }
        break;
      }
      case "tool_call_result": {
        if (isToolCallResultPayload(event.payload)) {
          return (
            <ToolCallCard
              toolName={event.payload.tool_name}
              args={{}}
              result={event.payload.result}
              error={event.payload.error}
              timestamp={event.timestamp}
            />
          );
        }
        break;
      }
      case "workflow_step_started": {
        if (isWorkflowStepStartedPayload(event.payload)) {
          return (
            <WorkflowStepBadge
              stepId={event.payload.step_id}
              status="active"
            />
          );
        }
        break;
      }
      case "workflow_step_completed": {
        if (isWorkflowStepCompletedPayload(event.payload)) {
          return (
            <WorkflowStepBadge
              stepId={event.payload.step_id}
              status="completed"
            />
          );
        }
        break;
      }
      case "agent_message_delta": {
        if (isAgentMessageDeltaPayload(event.payload)) {
          return (
            <div className="text-sm text-gray-700 dark:text-gray-300">
              {escapeHtml(event.payload.delta)}
            </div>
          );
        }
        break;
      }
      case "agent_message_end": {
        if (isAgentMessageEndPayload(event.payload)) {
          return (
            <div className="text-sm text-gray-700 dark:text-gray-300">
              {escapeHtml(event.payload.content)}
            </div>
          );
        }
        break;
      }
      case "agent_thought": {
        if (isAgentThoughtPayload(event.payload)) {
          return (
            <div className="text-sm italic text-gray-600 dark:text-gray-400">
              {escapeHtml(event.payload.content)}
            </div>
          );
        }
        break;
      }
      case "run_error": {
        if (isRunErrorPayload(event.payload)) {
          return (
            <div className="text-sm text-red-700 dark:text-red-400">
              {escapeHtml(event.payload.message)}
            </div>
          );
        }
        break;
      }
      default:
        return (
          <div className="text-xs text-gray-500 dark:text-gray-500">
            <pre>{sanitizeJson(event.payload)}</pre>
          </div>
        );
    }
    
    // Fallback if type guards fail
    return (
      <div className="text-xs text-gray-500 dark:text-gray-500">
        <pre>{sanitizeJson(event.payload)}</pre>
      </div>
    );
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

