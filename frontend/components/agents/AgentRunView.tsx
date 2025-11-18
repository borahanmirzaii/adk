"use client";

import { useState } from "react";
import { SplitPane } from "@/components/layout/SplitPane";
import { ChatPanel } from "./ChatPanel";
import { AgentTimeline } from "./AgentTimeline";
import { ToolInspector } from "./ToolInspector";
import { LiveConsole } from "./LiveConsole";
import { WorkflowGraph } from "./WorkflowGraph";
import { DebuggerSidebar } from "./DebuggerSidebar";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Wrench, Terminal, Workflow, Bug } from "lucide-react";
import { ErrorState } from "@/components/shared/ErrorState";
import { LoadingState } from "@/components/shared/LoadingState";

interface AgentRunViewProps {
  sessionId: string;
}

type InspectorTab = "tools" | "console" | "workflow" | "debugger";

export function AgentRunView({ sessionId }: AgentRunViewProps) {
  const [activeTab, setActiveTab] = useState<InspectorTab>("tools");
  const [error, setError] = useState<string | null>(null);

  if (!sessionId) {
    return (
      <div className="h-screen flex items-center justify-center">
        <ErrorState message="Invalid session ID" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="h-screen flex items-center justify-center">
        <ErrorState message={error} onRetry={() => setError(null)} />
      </div>
    );
  }

  return (
    <div className="h-screen w-full flex flex-col bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 px-4 py-3">
        <div className="flex items-center justify-between">
          <h1 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
            Agent Runtime
          </h1>
          <div className="text-sm text-gray-500 dark:text-gray-400">
            Session: <span className="font-mono">{sessionId}</span>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-hidden">
        <SplitPane
          defaultSizes={[25, 50, 25]}
          storageKey="agent-run-view-split"
          className="h-full"
        >
          {/* Left Panel: Chat */}
          <div className="h-full">
            <ChatPanel sessionId={sessionId} />
          </div>

          {/* Center Panel: Timeline */}
          <div className="h-full overflow-auto">
            <AgentTimeline sessionId={sessionId} />
          </div>

          {/* Right Panel: Inspector Tabs */}
          <div className="h-full flex flex-col">
            <Tabs
              value={activeTab}
              onValueChange={(value) => setActiveTab(value as InspectorTab)}
              className="h-full flex flex-col"
            >
              <TabsList className="w-full justify-start rounded-none border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900">
                <TabsTrigger value="tools" className="flex items-center gap-2">
                  <Wrench className="w-4 h-4" />
                  Tools
                </TabsTrigger>
                <TabsTrigger value="console" className="flex items-center gap-2">
                  <Terminal className="w-4 h-4" />
                  Console
                </TabsTrigger>
                <TabsTrigger value="workflow" className="flex items-center gap-2">
                  <Workflow className="w-4 h-4" />
                  Workflow
                </TabsTrigger>
                <TabsTrigger value="debugger" className="flex items-center gap-2">
                  <Bug className="w-4 h-4" />
                  Debugger
                </TabsTrigger>
              </TabsList>
              <div className="flex-1 overflow-hidden">
                <TabsContent value="tools" className="h-full m-0">
                  <ToolInspector sessionId={sessionId} />
                </TabsContent>
                <TabsContent value="console" className="h-full m-0">
                  <LiveConsole sessionId={sessionId} />
                </TabsContent>
                <TabsContent value="workflow" className="h-full m-0">
                  <WorkflowGraph sessionId={sessionId} />
                </TabsContent>
                <TabsContent value="debugger" className="h-full m-0">
                  <DebuggerSidebar sessionId={sessionId} />
                </TabsContent>
              </div>
            </Tabs>
          </div>
        </SplitPane>
      </div>
    </div>
  );
}

