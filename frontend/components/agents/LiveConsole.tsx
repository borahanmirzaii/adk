"use client";

import { useState, useEffect, useRef } from "react";
import { useAgentEvents } from "@/hooks/useAgentEvents";
import { CardSection } from "@/components/shared/CardSection";
import { Terminal, X } from "lucide-react";
import { cn } from "@/lib/utils";
import type { AgentEvent } from "@/types/events";

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
        const payload = event.payload as any;
        setLogs((prev) => [
          ...prev,
          {
            id: `log-${Date.now()}-${Math.random()}`,
            timestamp: new Date(event.timestamp),
            level: "debug",
            message: payload.content,
            source: `agent_thought:${payload.agent || "unknown"}`,
          },
        ]);
      },
      tool_call_delta: (event) => {
        const payload = event.payload as any;
        setLogs((prev) => [
          ...prev,
          {
            id: `log-${Date.now()}-${Math.random()}`,
            timestamp: new Date(event.timestamp),
            level: "info",
            message: payload.delta,
            source: "tool_call",
          },
        ]);
      },
      run_error: (event) => {
        const payload = event.payload as any;
        setLogs((prev) => [
          ...prev,
          {
            id: `log-${Date.now()}-${Math.random()}`,
            timestamp: new Date(event.timestamp),
            level: "error",
            message: payload.message,
            source: `error:${payload.agent || "unknown"}`,
          },
        ]);
      },
      agent_message_delta: (event) => {
        const payload = event.payload as any;
        setLogs((prev) => [
          ...prev,
          {
            id: `log-${Date.now()}-${Math.random()}`,
            timestamp: new Date(event.timestamp),
            level: "info",
            message: payload.delta,
            source: "agent_message",
          },
        ]);
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
      >
        {filteredLogs.length === 0 ? (
          <div className="text-gray-500 italic">No logs yet...</div>
        ) : (
          filteredLogs.map((log) => (
            <div
              key={log.id}
              className="mb-1 flex gap-2"
            >
              <span className="text-gray-500">
                {log.timestamp.toLocaleTimeString()}
              </span>
              <span className={cn("font-semibold", getLevelColor(log.level))}>
                [{log.level.toUpperCase()}]
              </span>
              <span className="text-gray-400">[{log.source}]</span>
              <span className="flex-1">{log.message}</span>
            </div>
          ))
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

