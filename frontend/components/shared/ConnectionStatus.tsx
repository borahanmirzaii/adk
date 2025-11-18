"use client";

import { Wifi, WifiOff } from "lucide-react";
import { cn } from "@/lib/utils";

interface ConnectionStatusProps {
  connected: boolean;
  className?: string;
}

export function ConnectionStatus({ connected, className }: ConnectionStatusProps) {
  return (
    <div
      className={cn(
        "flex items-center gap-2 text-xs",
        connected ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400",
        className
      )}
      title={connected ? "Connected" : "Disconnected"}
    >
      {connected ? (
        <Wifi className="w-4 h-4" />
      ) : (
        <WifiOff className="w-4 h-4" />
      )}
      <span>{connected ? "Connected" : "Disconnected"}</span>
    </div>
  );
}

