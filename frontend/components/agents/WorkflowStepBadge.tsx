"use client";

import { cn } from "@/lib/utils";
import { CheckCircle2, Circle, Loader2 } from "lucide-react";

interface WorkflowStepBadgeProps {
  stepId: string;
  status: "pending" | "active" | "completed";
  className?: string;
}

export function WorkflowStepBadge({
  stepId,
  status,
  className,
}: WorkflowStepBadgeProps) {
  const statusConfig = {
    pending: {
      bg: "bg-gray-100 dark:bg-gray-800",
      text: "text-gray-600 dark:text-gray-400",
      icon: Circle,
    },
    active: {
      bg: "bg-blue-100 dark:bg-blue-900",
      text: "text-blue-700 dark:text-blue-300",
      icon: Loader2,
    },
    completed: {
      bg: "bg-green-100 dark:bg-green-900",
      text: "text-green-700 dark:text-green-300",
      icon: CheckCircle2,
    },
  };

  const config = statusConfig[status];
  const Icon = config.icon;

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 px-2 py-1 rounded-md text-xs font-medium",
        config.bg,
        config.text,
        className
      )}
    >
      <Icon className="w-3 h-3" />
      {stepId}
    </span>
  );
}
