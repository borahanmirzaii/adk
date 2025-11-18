"use client";

import { useState, useMemo } from "react";
import { useAgentEvents } from "@/hooks/useAgentEvents";
import { CardSection } from "@/components/shared/CardSection";
import { ChevronDown, ChevronRight, Clock, AlertCircle, Wrench, Brain, Database } from "lucide-react";
import { cn } from "@/lib/utils";
import { motion, AnimatePresence } from "framer-motion";
import type { AgentEvent, RunErrorEvent } from "@/types/events";

interface DebuggerSidebarProps {
  sessionId: string;
}

interface StepInfo {
  stepId: string;
  type: string;
  startTime: Date;
  endTime?: Date;
  duration?: number;
}

export function DebuggerSidebar({ sessionId }: DebuggerSidebarProps) {
  const [expandedSections, setExpandedSections] = useState({
    steps: true,
    tools: true,
    errors: true,
    metadata: false,
  });
  const [steps, setSteps] = useState<StepInfo[]>([]);
  const [tools, setTools] = useState<Set<string>>(new Set());
  const [lastError, setLastError] = useState<RunErrorEvent | null>(null);
  const [sessionMetadata, setSessionMetadata] = useState<Record<string, any>>({});

  useAgentEvents(
    sessionId,
    {
      session_started: (event) => {
        setSessionMetadata((prev) => ({
          ...prev,
          sessionId: event.session_id,
          startTime: event.timestamp,
          agent: (event.payload as any).agent,
        }));
      },
      tool_call_started: (event) => {
        const payload = event.payload as any;
        setTools((prev) => new Set([...prev, payload.tool_name]));
        setSteps((prev) => [
          ...prev,
          {
            stepId: payload.tool_call_id,
            type: `tool:${payload.tool_name}`,
            startTime: new Date(event.timestamp),
          },
        ]);
      },
      tool_call_result: (event) => {
        const payload = event.payload as any;
        setSteps((prev) => {
          const updated = [...prev];
          const index = updated.findIndex((s) => s.stepId === payload.tool_call_id);
          if (index >= 0) {
            updated[index] = {
              ...updated[index],
              endTime: new Date(event.timestamp),
              duration:
                new Date(event.timestamp).getTime() -
                updated[index].startTime.getTime(),
            };
          }
          return updated;
        });
      },
      workflow_step_started: (event) => {
        const payload = event.payload as any;
        setSteps((prev) => [
          ...prev,
          {
            stepId: payload.step_id,
            type: `workflow:${payload.step_id}`,
            startTime: new Date(event.timestamp),
          },
        ]);
      },
      workflow_step_completed: (event) => {
        const payload = event.payload as any;
        setSteps((prev) => {
          const updated = [...prev];
          const index = updated.findIndex((s) => s.stepId === payload.step_id);
          if (index >= 0) {
            updated[index] = {
              ...updated[index],
              endTime: new Date(event.timestamp),
              duration:
                new Date(event.timestamp).getTime() -
                updated[index].startTime.getTime(),
            };
          }
          return updated;
        });
      },
      run_error: (event) => {
        setLastError(event as RunErrorEvent);
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

  const formatDuration = (ms?: number) => {
    if (!ms) return "-";
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(2)}s`;
  };

  return (
    <CardSection title="Debugger" className="h-full flex flex-col">
      <div className="flex-1 overflow-y-auto space-y-4">
        {/* Steps List */}
        <div className="border border-gray-200 dark:border-gray-800 rounded-lg overflow-hidden">
          <button
            onClick={() => toggleSection("steps")}
            className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
          >
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-gray-500" />
              <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                Steps ({steps.length})
              </span>
            </div>
            {expandedSections.steps ? (
              <ChevronDown className="w-4 h-4 text-gray-500" />
            ) : (
              <ChevronRight className="w-4 h-4 text-gray-500" />
            )}
          </button>
          <AnimatePresence>
            {expandedSections.steps && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: "auto", opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.2 }}
                className="overflow-hidden"
              >
                <div className="px-4 py-3 bg-gray-50 dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800 space-y-2 max-h-64 overflow-y-auto">
                  {steps.length === 0 ? (
                    <div className="text-xs text-gray-500">No steps yet</div>
                  ) : (
                    steps.map((step, index) => (
                      <div
                        key={`${step.stepId}-${index}`}
                        className="text-xs p-2 bg-white dark:bg-gray-800 rounded border border-gray-200 dark:border-gray-700"
                      >
                        <div className="font-medium text-gray-900 dark:text-gray-100">
                          {step.stepId}
                        </div>
                        <div className="text-gray-600 dark:text-gray-400 mt-1">
                          {step.type}
                        </div>
                        <div className="text-gray-500 mt-1">
                          Duration: {formatDuration(step.duration)}
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Tools List */}
        <div className="border border-gray-200 dark:border-gray-800 rounded-lg overflow-hidden">
          <button
            onClick={() => toggleSection("tools")}
            className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
          >
            <div className="flex items-center gap-2">
              <Wrench className="w-4 h-4 text-gray-500" />
              <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                Tools ({tools.size})
              </span>
            </div>
            {expandedSections.tools ? (
              <ChevronDown className="w-4 h-4 text-gray-500" />
            ) : (
              <ChevronRight className="w-4 h-4 text-gray-500" />
            )}
          </button>
          <AnimatePresence>
            {expandedSections.tools && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: "auto", opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.2 }}
                className="overflow-hidden"
              >
                <div className="px-4 py-3 bg-gray-50 dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800 space-y-1">
                  {tools.size === 0 ? (
                    <div className="text-xs text-gray-500">No tools used yet</div>
                  ) : (
                    Array.from(tools).map((tool) => (
                      <div
                        key={tool}
                        className="text-xs px-2 py-1 bg-white dark:bg-gray-800 rounded"
                      >
                        {tool}
                      </div>
                    ))
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Error State */}
        {lastError && (
          <div className="border border-red-200 dark:border-red-800 rounded-lg overflow-hidden">
            <button
              onClick={() => toggleSection("errors")}
              className="w-full px-4 py-3 flex items-center justify-between hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
            >
              <div className="flex items-center gap-2">
                <AlertCircle className="w-4 h-4 text-red-500" />
                <span className="text-sm font-medium text-red-700 dark:text-red-400">
                  Last Error
                </span>
              </div>
              {expandedSections.errors ? (
                <ChevronDown className="w-4 h-4 text-red-500" />
              ) : (
                <ChevronRight className="w-4 h-4 text-red-500" />
              )}
            </button>
            <AnimatePresence>
              {expandedSections.errors && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: "auto", opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.2 }}
                  className="overflow-hidden"
                >
                  <div className="px-4 py-3 bg-red-50 dark:bg-red-900/20 border-t border-red-200 dark:border-red-800">
                    <div className="text-xs space-y-1">
                      <div>
                        <span className="font-medium">Type:</span>{" "}
                        {lastError.payload.error_type}
                      </div>
                      <div>
                        <span className="font-medium">Message:</span>{" "}
                        {lastError.payload.message}
                      </div>
                      {lastError.payload.step && (
                        <div>
                          <span className="font-medium">Step:</span>{" "}
                          {lastError.payload.step}
                        </div>
                      )}
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        )}

        {/* Metadata */}
        <div className="border border-gray-200 dark:border-gray-800 rounded-lg overflow-hidden">
          <button
            onClick={() => toggleSection("metadata")}
            className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
          >
            <div className="flex items-center gap-2">
              <Database className="w-4 h-4 text-gray-500" />
              <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                Run Metadata
              </span>
            </div>
            {expandedSections.metadata ? (
              <ChevronDown className="w-4 h-4 text-gray-500" />
            ) : (
              <ChevronRight className="w-4 h-4 text-gray-500" />
            )}
          </button>
          <AnimatePresence>
            {expandedSections.metadata && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: "auto", opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.2 }}
                className="overflow-hidden"
              >
                <div className="px-4 py-3 bg-gray-50 dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800">
                  <div className="text-xs space-y-1">
                    {Object.entries(sessionMetadata).map(([key, value]) => (
                      <div key={key}>
                        <span className="font-medium">{key}:</span>{" "}
                        {typeof value === "object"
                          ? JSON.stringify(value)
                          : String(value)}
                      </div>
                    ))}
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </CardSection>
  );
}

