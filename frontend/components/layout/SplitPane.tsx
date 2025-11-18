"use client";

import { useState, useEffect, useRef, ReactNode } from "react";
import { GripVertical } from "lucide-react";
import { cn } from "@/lib/utils";

interface SplitPaneProps {
  children: [ReactNode, ReactNode, ReactNode?];
  defaultSizes?: [number, number, number?];
  minSize?: number;
  storageKey?: string;
  className?: string;
}

export function SplitPane({
  children,
  defaultSizes = [30, 40, 30],
  minSize = 10,
  storageKey,
  className,
}: SplitPaneProps) {
  const [sizes, setSizes] = useState<number[]>(() => {
    if (storageKey && typeof window !== "undefined") {
      const saved = localStorage.getItem(storageKey);
      if (saved) {
        try {
          return JSON.parse(saved);
        } catch {
          // fallback to defaults
        }
      }
    }
    return defaultSizes.slice(0, children.length);
  });

  const containerRef = useRef<HTMLDivElement>(null);
  const [isDragging, setIsDragging] = useState<number | null>(null);
  const startPosRef = useRef<{ x: number; sizes: number[] } | null>(null);

  useEffect(() => {
    if (storageKey && typeof window !== "undefined") {
      localStorage.setItem(storageKey, JSON.stringify(sizes));
    }
  }, [sizes, storageKey]);

  const handleMouseDown = (index: number) => {
    setIsDragging(index);
  };

  useEffect(() => {
    if (isDragging === null || !containerRef.current) return;

    const handleMouseMove = (e: MouseEvent) => {
      if (!containerRef.current || !startPosRef.current) return;

      const containerRect = containerRef.current.getBoundingClientRect();
      const totalWidth = containerRect.width;
      const deltaX = e.clientX - startPosRef.current.x;
      const deltaPercent = (deltaX / totalWidth) * 100;

      const newSizes = [...startPosRef.current.sizes];
      const leftIndex = isDragging;
      const rightIndex = isDragging + 1;

      if (rightIndex >= newSizes.length) return;

      const newLeft = newSizes[leftIndex] + deltaPercent;
      const newRight = newSizes[rightIndex] - deltaPercent;

      if (newLeft >= minSize && newRight >= minSize) {
        newSizes[leftIndex] = newLeft;
        newSizes[rightIndex] = newRight;
        setSizes(newSizes);
      }
    };

    const handleMouseUp = () => {
      setIsDragging(null);
      startPosRef.current = null;
    };

    if (isDragging !== null && containerRef.current) {
      startPosRef.current = {
        x: containerRef.current.getBoundingClientRect().left + (containerRef.current.getBoundingClientRect().width * sizes.slice(0, isDragging + 1).reduce((a, b) => a + b, 0) / 100),
        sizes: [...sizes],
      };
    }

    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("mouseup", handleMouseUp);

    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseup", handleMouseUp);
    };
  }, [isDragging, sizes, minSize]);

  return (
    <div
      ref={containerRef}
      className={cn("flex h-full w-full relative", className)}
    >
      {children.map((child, index) => (
        <div key={index}>
          <div
            style={{ width: `${sizes[index]}%` }}
            className="h-full overflow-auto"
          >
            {child}
          </div>
          {index < children.length - 1 && (
            <div
              className={cn(
                "w-1 bg-gray-200 dark:bg-gray-700 cursor-col-resize hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors flex items-center justify-center relative z-10",
                isDragging === index && "bg-blue-500"
              )}
              onMouseDown={() => handleMouseDown(index)}
            >
              <GripVertical className="w-4 h-4 text-gray-400" />
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

