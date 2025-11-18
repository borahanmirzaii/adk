/**
 * @jest-environment jsdom
 */

import { render, screen } from "@testing-library/react";
import { WorkflowStepBadge } from "@/components/agents/WorkflowStepBadge";

describe("WorkflowStepBadge", () => {
  it("should render step ID", () => {
    render(<WorkflowStepBadge stepId="step1" status="pending" />);
    expect(screen.getByText("step1")).toBeInTheDocument();
  });

  it("should apply correct styles for pending status", () => {
    const { container } = render(
      <WorkflowStepBadge stepId="step1" status="pending" />
    );
    expect(container.firstChild).toHaveClass("bg-gray-100");
  });

  it("should apply correct styles for active status", () => {
    const { container } = render(
      <WorkflowStepBadge stepId="step1" status="active" />
    );
    expect(container.firstChild).toHaveClass("bg-blue-100");
  });

  it("should apply correct styles for completed status", () => {
    const { container } = render(
      <WorkflowStepBadge stepId="step1" status="completed" />
    );
    expect(container.firstChild).toHaveClass("bg-green-100");
  });
});

