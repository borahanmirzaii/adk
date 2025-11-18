"use client";

import {
  MessageSquare,
  Wrench,
  Workflow,
  Brain,
  AlertCircle,
  RefreshCw,
  Search,
  Zap,
  Activity,
  XCircle,
} from "lucide-react";
import type { EventType } from "@/types/events";
import { cn } from "@/lib/utils";

interface EventIconProps {
  type: EventType;
  className?: string;
}

export function EventIcon({ type, className }: EventIconProps) {
  const iconProps = {
    className: cn("w-4 h-4", className),
  };

  if (type.startsWith("session_")) {
    return <Activity {...iconProps} />;
  }
  if (type.startsWith("agent_message_")) {
    return <MessageSquare {...iconProps} />;
  }
  if (type.startsWith("tool_call_")) {
    return <Wrench {...iconProps} />;
  }
  if (type.startsWith("workflow_")) {
    return <Workflow {...iconProps} />;
  }
  if (type === "agent_thought") {
    return <Brain {...iconProps} />;
  }
  if (type === "run_error") {
    return <AlertCircle {...iconProps} />;
  }
  if (type === "run_retry") {
    return <RefreshCw {...iconProps} />;
  }
  if (type === "run_interrupted") {
    return <XCircle {...iconProps} />;
  }
  if (type.startsWith("retrieval_")) {
    return <Search {...iconProps} />;
  }
  if (type.startsWith("automation_")) {
    return <Zap {...iconProps} />;
  }
  if (type === "metrics_update") {
    return <Activity {...iconProps} />;
  }

  return <Activity {...iconProps} />;
}
