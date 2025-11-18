/**
 * @jest-environment jsdom
 */

import { render } from "@testing-library/react";
import { EventIcon } from "@/components/agents/EventIcon";

describe("EventIcon", () => {
  it("should render icon for session events", () => {
    const { container } = render(<EventIcon type="session_started" />);
    expect(container.firstChild).toBeInTheDocument();
  });

  it("should render icon for tool call events", () => {
    const { container } = render(<EventIcon type="tool_call_started" />);
    expect(container.firstChild).toBeInTheDocument();
  });

  it("should render icon for workflow events", () => {
    const { container } = render(<EventIcon type="workflow_started" />);
    expect(container.firstChild).toBeInTheDocument();
  });

  it("should render icon for error events", () => {
    const { container } = render(<EventIcon type="run_error" />);
    expect(container.firstChild).toBeInTheDocument();
  });

  it("should apply custom className", () => {
    const { container } = render(
      <EventIcon type="session_started" className="custom-class" />
    );
    expect(container.firstChild).toHaveClass("custom-class");
  });
});

