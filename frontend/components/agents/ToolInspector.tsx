"use client";

import { useState, useEffect } from "react";
import { useAgentEvents } from "@/hooks/useAgentEvents";
import { CardSection } from "@/components/shared/CardSection";
import { LoadingState } from "@/components/shared/LoadingState";
import { Code, ChevronDown, ChevronUp } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";
import type { ToolCallStartedEvent, ToolCallResultEvent } from "@/types/events";
import {
  isToolCallStartedPayload,
  isToolCallResultPayload,
} from "@/lib/typeGuards";
import { sanitizeJson } from "@/lib/sanitize";

interface ToolInspectorProps {
  sessionId: string;
}

interface ToolCallData {
  tool_call_id: string;
  tool_name: string;
  args: Record<string, any>;
  result?: any;
  error?: string;
  timestamp: string;
}

export function ToolInspector({ sessionId }: ToolInspectorProps) {
  const [lastToolCall, setLastToolCall] = useState<ToolCallData | null>(null);
  const [expandedSections, setExpandedSections] = useState({
    args: true,
    result: true,
    error: false,
  });

  useAgentEvents(
    sessionId,
    {
      tool_call_started: (event) => {
        if (isToolCallStartedPayload(event.payload)) {
          setLastToolCall({
            tool_call_id: event.payload.tool_call_id,
            tool_name: event.payload.tool_name,
            args: event.payload.args,
            timestamp: event.timestamp,
          });
          setExpandedSections({ args: true, result: false, error: false });
        }
      },
      tool_call_result: (event) => {
        if (isToolCallResultPayload(event.payload)) {
          setLastToolCall((prev) => {
            if (prev?.tool_call_id === event.payload.tool_call_id) {
              return {
                ...prev,
                result: event.payload.result,
                error: event.payload.error,
              };
            }
            return prev;
          });
          if (event.payload.error) {
            setExpandedSections((prev) => ({ ...prev, error: true }));
          } else {
            setExpandedSections((prev) => ({ ...prev, result: true }));
          }
        }
      },
    },
    undefined
  );

  const toggleSection = (section: keyof typeof expandedSections) => {
    setExpandedSections((prev) => ({
      ...prev,
      [section]: !prev[section],
    }));
  };

  if (!lastToolCall) {
    return (
      <CardSection title="Tool Inspector">
        <LoadingState message="Waiting for tool calls..." />
      </CardSection>
    );
  }

  return (
    <CardSection title="Tool Inspector" className="h-full flex flex-col">
      <div className="flex-1 overflow-y-auto">
        <div className="space-y-4">
          {/* Tool Name */}
          <div className="flex items-center gap-2">
            <Code className="w-5 h-5 text-blue-600 dark:text-blue-400" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
              {lastToolCall.tool_name}
            </h3>
          </div>

          {/* Arguments Section */}
          <div className="border border-gray-200 dark:border-gray-800 rounded-lg overflow-hidden">
            <button
              onClick={() => toggleSection("args")}
              className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
              aria-expanded={expandedSections.args}
              aria-controls="tool-args-content"
              aria-label={`${expandedSections.args ? "Collapse" : "Expand"} arguments`}
            >
              <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                Arguments
              </span>
              {expandedSections.args ? (
                <ChevronUp className="w-4 h-4 text-gray-500" />
              ) : (
                <ChevronDown className="w-4 h-4 text-gray-500" />
              )}
            </button>
            <AnimatePresence>
              {expandedSections.args && (
                <motion.div
                  id="tool-args-content"
                  role="region"
                  aria-label="Tool arguments"
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: "auto", opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.2 }}
                  className="overflow-hidden"
                >
                  <div className="px-4 py-3 bg-gray-50 dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800">
                    <pre className="text-xs overflow-x-auto" role="textbox" aria-readonly="true">
                      {sanitizeJson(lastToolCall.args)}
                    </pre>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Result Section */}
          {lastToolCall.result !== undefined && (
            <div className="border border-gray-200 dark:border-gray-800 rounded-lg overflow-hidden">
              <button
                onClick={() => toggleSection("result")}
                className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
              >
                <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                  Result
                </span>
                {expandedSections.result ? (
                  <ChevronUp className="w-4 h-4 text-gray-500" />
                ) : (
                  <ChevronDown className="w-4 h-4 text-gray-500" />
                )}
              </button>
              <AnimatePresence>
                {expandedSections.result && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.2 }}
                    className="overflow-hidden"
                  >
                    <div className="px-4 py-3 bg-gray-50 dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800">
                      <pre className="text-xs overflow-x-auto">
                        {sanitizeJson(lastToolCall.result)}
                      </pre>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          )}

          {/* Error Section */}
          {lastToolCall.error && (
            <div className="border border-red-200 dark:border-red-800 rounded-lg overflow-hidden">
              <button
                onClick={() => toggleSection("error")}
                className="w-full px-4 py-3 flex items-center justify-between hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
              >
                <span className="text-sm font-medium text-red-700 dark:text-red-400">
                  Error
                </span>
                {expandedSections.error ? (
                  <ChevronUp className="w-4 h-4 text-red-500" />
                ) : (
                  <ChevronDown className="w-4 h-4 text-red-500" />
                )}
              </button>
              <AnimatePresence>
                {expandedSections.error && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.2 }}
                    className="overflow-hidden"
                  >
                    <div className="px-4 py-3 bg-red-50 dark:bg-red-900/20 border-t border-red-200 dark:border-red-800">
                      <pre className="text-xs overflow-x-auto text-red-700 dark:text-red-400">
                        {sanitizeJson(lastToolCall.error)}
                      </pre>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          )}

          {/* Metadata */}
          <div className="text-xs text-gray-500 dark:text-gray-400">
            Tool Call ID: {lastToolCall.tool_call_id}
            <br />
            Timestamp: {new Date(lastToolCall.timestamp).toLocaleString()}
          </div>
        </div>
      </div>
    </CardSection>
  );
}

