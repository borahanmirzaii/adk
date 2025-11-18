"use client";

import { AgentRunView } from "@/components/agents/AgentRunView";
import { ErrorBoundary } from "@/components/shared/ErrorBoundary";

interface PageProps {
  params: { sessionId: string };
}

export default function AgentSessionPage({ params }: PageProps) {
  const { sessionId } = params;

  if (!sessionId) {
    return (
      <div className="h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
            Invalid Session
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            No session ID provided
          </p>
        </div>
      </div>
    );
  }

  return (
    <ErrorBoundary>
      <AgentRunView sessionId={sessionId} />
    </ErrorBoundary>
  );
}

