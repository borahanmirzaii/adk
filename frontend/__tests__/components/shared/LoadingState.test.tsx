/**
 * @jest-environment jsdom
 */

import { render, screen } from "@testing-library/react";
import { LoadingState } from "@/components/shared/LoadingState";

describe("LoadingState", () => {
  it("should render default message", () => {
    render(<LoadingState />);

    expect(screen.getByText("Loading...")).toBeInTheDocument();
  });

  it("should render custom message", () => {
    render(<LoadingState message="Custom loading..." />);

    expect(screen.getByText("Custom loading...")).toBeInTheDocument();
  });

  it("should apply custom className", () => {
    const { container } = render(
      <LoadingState className="custom-class" />
    );

    expect(container.firstChild).toHaveClass("custom-class");
  });
});

