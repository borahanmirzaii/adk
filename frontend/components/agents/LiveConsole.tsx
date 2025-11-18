"use client";

import { useState, useEffect, useRef } from "react";
import { useAgentEvents } from "@/hooks/useAgentEvents";
import { CardSection } from "@/components/shared/CardSection";
import { Terminal, X } from "lucide-react";
import { cn } from "@/lib/utils";
import type { AgentEvent } from "@/types/events";
import { MAX_CONSOLE_LOGS } from "@/lib/constants";

interface ConsoleLog {
  id: string;
  timestamp: Date;
  level: "info" | "warn" | "error" | "debug";
  message: string;
  source: string;
}

interface LiveConsoleProps {
  sessionId: string;
}

export function LiveConsole({ sessionId }: LiveConsoleProps) {
  const [logs, setLogs] = useState<ConsoleLog[]>([]);
  const [autoScroll, setAutoScroll] = useState(true);
  const [filter, setFilter] = useState<"all" | "info" | "warn" | "error" | "debug">("all");
  const logsEndRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    if (autoScroll && logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [logs, autoScroll]);

  // Check if user scrolled up
  const handleScroll = () => {
    if (!containerRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = containerRef.current;
    const isAtBottom = scrollTop + clientHeight >= scrollHeight - 10;
    setAutoScroll(isAtBottom);
  };

  useAgentEvents(
    sessionId,
    {
      agent_thought: (event) => {
        if (isAgentThoughtPayload(event.payload)) {
          setLogs((prev) => {
            const updated = [
              ...prev,
              {
                id: `log-${Date.now()}-${Math.random()}`,
                timestamp: new Date(event.timestamp),
                level: "debug" as const,
                message: event.payload.content,
                source: `agent_thought:${event.payload.agent || "unknown"}`,
              },
            ];
            return updated.slice(-MAX_CONSOLE_LOGS);
          });
        }
      },
      tool_call_delta: (event) => {
        // ToolCallDeltaPayload has delta field
        if (
          typeof event.payload === "object" &&
          event.payload !== null &&
          "delta" in event.payload &&
          typeof (event.payload as any).delta === "string"
        ) {
          setLogs((prev) => {
            const updated = [
              ...prev,
              {
                id: `log-${Date.now()}-${Math.random()}`,
                timestamp: new Date(event.timestamp),
                level: "info" as const,
                message: (event.payload as any).delta,
                source: "tool_call",
              },
            ];
            return updated.slice(-MAX_CONSOLE_LOGS);
          });
        }
      },
      run_error: (event) => {
        if (isRunErrorPayload(event.payload)) {
          setLogs((prev) => {
            const updated = [
              ...prev,
              {
                id: `log-${Date.now()}-${Math.random()}`,
                timestamp: new Date(event.timestamp),
                level: "error" as const,
                message: event.payload.message,
                source: `error:${event.payload.agent || "unknown"}`,
              },
            ];
            return updated.slice(-MAX_CONSOLE_LOGS);
          });
        }
      },
      agent_message_delta: (event) => {
        if (isAgentMessageDeltaPayload(event.payload)) {
          setLogs((prev) => {
            const updated = [
              ...prev,
              {
                id: `log-${Date.now()}-${Math.random()}`,
                timestamp: new Date(event.timestamp),
                level: "info" as const,
                message: event.payload.delta,
                source: "agent_message",
              },
            ];
            return updated.slice(-MAX_CONSOLE_LOGS);
          });
        }
      },
    },
    (event) => {
      // Log all events for debugging
      if (process.env.NODE_ENV === "development") {
        console.log("[Console] Event:", event.type, event);
      }
    }
  );

  const filteredLogs = logs.filter((log) => {
    if (filter === "all") return true;
    return log.level === filter;
  });

  // Virtualization setup
  const virtualizer = useVirtualizer({
    count: filteredLogs.length,
    getScrollElement: () => containerRef.current,
    estimateSize: () => 24, // Estimated height per log line
    overscan: 10, // Render 10 extra items outside viewport
  });

  const getLevelColor = (level: ConsoleLog["level"]) => {
    switch (level) {
      case "error":
        return "text-red-400";
      case "warn":
        return "text-yellow-400";
      case "debug":
        return "text-purple-400";
      default:
        return "text-gray-300";
    }
  };

  const clearLogs = () => {
    setLogs([]);
  };

  return (
    <CardSection
      title="Live Console"
      headerActions={
        <div className="flex items-center gap-2">
          <select
            value={filter}
            onChange={(e) =>
              setFilter(e.target.value as typeof filter)
            }
            className="text-xs bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded px-2 py-1"
            aria-label="Filter console logs by level"
          >
            <option value="all">All</option>
            <option value="info">Info</option>
            <option value="warn">Warn</option>
            <option value="error">Error</option>
            <option value="debug">Debug</option>
          </select>
          <button
            onClick={clearLogs}
            className="text-xs text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100"
            title="Clear logs"
            aria-label="Clear all console logs"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      }
      className="h-full flex flex-col"
    >
      <div
        ref={containerRef}
        onScroll={handleScroll}
        className="flex-1 overflow-y-auto bg-gray-900 text-green-400 font-mono text-xs p-4 rounded"
        style={{ contain: "strict" }}
        role="log"
        aria-label="Console output"
        aria-live="polite"
        aria-atomic="false"
      >
        {filteredLogs.length === 0 ? (
          <div className="text-gray-500 italic">No logs yet...</div>
        ) : (
          <div
            style={{
              height: `${virtualizer.getTotalSize()}px`,
              width: "100%",
              position: "relative",
            }}
          >
            {virtualizer.getVirtualItems().map((virtualItem) => {
              const log = filteredLogs[virtualItem.index];
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
                  className="mb-1 flex gap-2 px-4"
                >
                  <span className="text-gray-500">
                    {log.timestamp.toLocaleTimeString()}
                  </span>
                  <span className={cn("font-semibold", getLevelColor(log.level))}>
                    [{log.level.toUpperCase()}]
                  </span>
                  <span className="text-gray-400">[{log.source}]</span>
                  <span className="flex-1">{sanitizeConsoleMessage(log.message)}</span>
                </div>
              );
            })}
          </div>
        )}
        <div ref={logsEndRef} />
      </div>
      {!autoScroll && (
        <div className="mt-2 text-xs text-center text-gray-500">
          <button
            onClick={() => {
              setAutoScroll(true);
              logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
            }}
            className="text-blue-600 dark:text-blue-400 hover:underline"
          >
            Scroll to bottom
          </button>
        </div>
      )}
    </CardSection>
  );
}

