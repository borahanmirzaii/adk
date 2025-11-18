"use client";

import { ReactNode } from "react";
import { cn } from "@/lib/utils";

interface CardSectionProps {
  title?: string;
  children: ReactNode;
  className?: string;
  headerActions?: ReactNode;
}

export function CardSection({
  title,
  children,
  className,
  headerActions,
}: CardSectionProps) {
  return (
    <div
      className={cn(
        "bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-lg shadow-sm",
        className
      )}
    >
      {title && (
        <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-800 flex items-center justify-between">
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            {title}
          </h3>
          {headerActions && <div>{headerActions}</div>}
        </div>
      )}
      <div className="p-4">{children}</div>
    </div>
  );
}

