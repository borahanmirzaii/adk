"use client";

import { useState } from "react";
import { ChevronDown, ChevronRight, Code } from "lucide-react";
import { cn } from "@/lib/utils";
import { motion, AnimatePresence } from "framer-motion";

interface ToolCallCardProps {
  toolName: string;
  args: Record<string, any>;
  result?: any;
  error?: string;
  timestamp: string;
}

export function ToolCallCard({
  toolName,
  args,
  result,
  error,
  timestamp,
}: ToolCallCardProps) {
  const [expanded, setExpanded] = useState(false);
  const cardId = `tool-call-${toolName}-${timestamp}`;

  return (
    <div className="border border-gray-200 dark:border-gray-800 rounded-lg overflow-hidden">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
        aria-expanded={expanded}
        aria-controls={cardId}
        aria-label={`${expanded ? "Collapse" : "Expand"} tool call ${toolName}`}
      >
        <div className="flex items-center gap-3">
          {expanded ? (
            <ChevronDown className="w-4 h-4 text-gray-500" />
          ) : (
            <ChevronRight className="w-4 h-4 text-gray-500" />
          )}
          <Code className="w-4 h-4 text-blue-600 dark:text-blue-400" />
          <span className="font-medium text-sm text-gray-900 dark:text-gray-100">
            {toolName}
          </span>
          {error && (
            <span className="text-xs text-red-600 dark:text-red-400">
              (Error)
            </span>
          )}
        </div>
        <span className="text-xs text-gray-500">
          {new Date(timestamp).toLocaleTimeString()}
        </span>
      </button>
      <AnimatePresence>
        {expanded && (
          <motion.div
            id={cardId}
            role="region"
            aria-labelledby={`tool-call-header-${cardId}`}
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="px-4 py-3 border-t border-gray-200 dark:border-gray-800 space-y-3">
              <div>
                <h4 className="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-2">
                  Arguments:
                </h4>
                <pre className="text-xs bg-gray-50 dark:bg-gray-900 p-2 rounded overflow-x-auto">
                  {JSON.stringify(args, null, 2)}
                </pre>
              </div>
              {result !== undefined && (
                <div>
                  <h4 className="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-2">
                    Result:
                  </h4>
                  <pre className="text-xs bg-gray-50 dark:bg-gray-900 p-2 rounded overflow-x-auto">
                    {JSON.stringify(result, null, 2)}
                  </pre>
                </div>
              )}
              {error && (
                <div>
                  <h4 className="text-xs font-semibold text-red-700 dark:text-red-300 mb-2">
                    Error:
                  </h4>
                  <pre className="text-xs bg-red-50 dark:bg-red-900/20 p-2 rounded overflow-x-auto text-red-700 dark:text-red-400">
                    {error}
                  </pre>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
