"use client";

import { useState, useMemo } from "react";
import { useAgentEvents } from "@/hooks/useAgentEvents";
import { CardSection } from "@/components/shared/CardSection";
import { LoadingState } from "@/components/shared/LoadingState";
import { Workflow, ArrowRight } from "lucide-react";
import { cn } from "@/lib/utils";
import type {
  WorkflowStartedEvent,
  WorkflowStepStartedEvent,
  WorkflowStepCompletedEvent,
  WorkflowTransitionEvent,
  WorkflowCompletedEvent,
} from "@/types/events";
import {
  isWorkflowStepStartedPayload,
  isWorkflowStepCompletedPayload,
} from "@/lib/typeGuards";

interface WorkflowGraphProps {
  sessionId: string;
}

interface WorkflowStep {
  id: string;
  description: string;
  status: "pending" | "active" | "completed";
  startTime?: Date;
  endTime?: Date;
}

interface WorkflowState {
  workflowId?: string;
  runId?: string;
  steps: Map<string, WorkflowStep>;
  transitions: Array<{ from: string; to: string; reason: string }>;
  currentStep?: string;
}

export function WorkflowGraph({ sessionId }: WorkflowGraphProps) {
  const [workflowState, setWorkflowState] = useState<WorkflowState>({
    steps: new Map(),
    transitions: [],
  });
  const [selectedStep, setSelectedStep] = useState<string | null>(null);

  useAgentEvents(
    sessionId,
    {
      workflow_started: (event) => {
        const payload = (event as WorkflowStartedEvent).payload;
        setWorkflowState((prev) => ({
          ...prev,
          workflowId: payload.workflow,
          runId: payload.run_id,
          steps: new Map(),
          transitions: [],
        }));
      },
      workflow_step_started: (event) => {
        if (isWorkflowStepStartedPayload(event.payload)) {
          setWorkflowState((prev) => {
            const newSteps = new Map(prev.steps);
            newSteps.set(event.payload.step_id, {
              id: event.payload.step_id,
              description: event.payload.description,
              status: "active",
              startTime: new Date(event.timestamp),
            });
            return {
              ...prev,
              steps: newSteps,
              currentStep: event.payload.step_id,
            };
          });
        }
      },
      workflow_step_completed: (event) => {
        if (isWorkflowStepCompletedPayload(event.payload)) {
          setWorkflowState((prev) => {
            const newSteps = new Map(prev.steps);
            const step = newSteps.get(event.payload.step_id);
            if (step) {
              newSteps.set(event.payload.step_id, {
                ...step,
                status: "completed",
                endTime: new Date(event.timestamp),
              });
            }
            return {
              ...prev,
              steps: newSteps,
              currentStep: undefined,
            };
          });
        }
      },
      workflow_transition: (event) => {
        const payload = (event as WorkflowTransitionEvent).payload;
        setWorkflowState((prev) => ({
          ...prev,
          transitions: [
            ...prev.transitions,
            {
              from: payload.from_step,
              to: payload.to_step,
              reason: payload.reason,
            },
          ],
        }));
      },
      workflow_completed: (event) => {
        const payload = (event as WorkflowCompletedEvent).payload;
        setWorkflowState((prev) => ({
          ...prev,
          currentStep: undefined,
        }));
      },
    },
    undefined
  );

  const stepsArray = useMemo(() => {
    return Array.from(workflowState.steps.values());
  }, [workflowState.steps]);

  if (stepsArray.length === 0) {
    return (
      <CardSection title="Workflow Graph">
        <LoadingState message="Waiting for workflow events..." />
      </CardSection>
    );
  }

  const getStepStatusColor = (status: WorkflowStep["status"]) => {
    switch (status) {
      case "completed":
        return "bg-green-500 border-green-600";
      case "active":
        return "bg-blue-500 border-blue-600 animate-pulse";
      default:
        return "bg-gray-300 border-gray-400";
    }
  };

  return (
    <CardSection title="Workflow Graph" className="h-full flex flex-col">
      <div className="flex-1 overflow-auto p-4">
        <div className="flex flex-col gap-4">
          {workflowState.workflowId && (
            <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">
              Workflow: <span className="font-semibold">{workflowState.workflowId}</span>
              {workflowState.runId && (
                <> | Run ID: <span className="font-mono text-xs">{workflowState.runId}</span></>
              )}
            </div>
          )}

          {/* Horizontal timeline layout */}
          <div className="flex items-center gap-2 overflow-x-auto pb-4">
            {stepsArray.map((step, index) => (
              <div key={step.id} className="flex items-center gap-2 flex-shrink-0">
                <div className="flex flex-col items-center">
                  <button
                    onClick={() =>
                      setSelectedStep(selectedStep === step.id ? null : step.id)
                    }
                    className={cn(
                      "w-16 h-16 rounded-full border-2 flex items-center justify-center transition-all cursor-pointer hover:scale-110",
                      getStepStatusColor(step.status),
                      selectedStep === step.id && "ring-4 ring-blue-300"
                    )}
                    title={step.description}
                    aria-label={`Workflow step ${step.id}: ${step.description}`}
                    aria-pressed={selectedStep === step.id}
                  >
                    <Workflow className="w-6 h-6 text-white" />
                  </button>
                  <div className="mt-2 text-xs text-center max-w-20">
                    <div className="font-medium text-gray-900 dark:text-gray-100 truncate">
                      {step.id}
                    </div>
                    {step.startTime && (
                      <div className="text-gray-500 text-[10px]">
                        {step.startTime.toLocaleTimeString()}
                      </div>
                    )}
                  </div>
                </div>
                {index < stepsArray.length - 1 && (
                  <ArrowRight className="w-6 h-6 text-gray-400 flex-shrink-0" />
                )}
              </div>
            ))}
          </div>

          {/* Selected step details */}
          {selectedStep && (
            <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
              <h4 className="font-semibold text-sm mb-2">
                Step: {selectedStep}
              </h4>
              {workflowState.steps.get(selectedStep) && (
                <div className="space-y-2 text-xs">
                  <div>
                    <span className="text-gray-600 dark:text-gray-400">
                      Description:
                    </span>{" "}
                    <span className="text-gray-900 dark:text-gray-100">
                      {workflowState.steps.get(selectedStep)?.description}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-600 dark:text-gray-400">
                      Status:
                    </span>{" "}
                    <span className="font-semibold">
                      {workflowState.steps.get(selectedStep)?.status}
                    </span>
                  </div>
                  {workflowState.steps.get(selectedStep)?.startTime && (
                    <div>
                      <span className="text-gray-600 dark:text-gray-400">
                        Started:
                      </span>{" "}
                      <span>
                        {workflowState.steps.get(selectedStep)?.startTime?.toLocaleString()}
                      </span>
                    </div>
                  )}
                  {workflowState.steps.get(selectedStep)?.endTime && (
                    <div>
                      <span className="text-gray-600 dark:text-gray-400">
                        Completed:
                      </span>{" "}
                      <span>
                        {workflowState.steps.get(selectedStep)?.endTime?.toLocaleString()}
                      </span>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </CardSection>
  );
}

