/**
 * @jest-environment jsdom
 */

import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ErrorState } from "@/components/shared/ErrorState";

describe("ErrorState", () => {
  it("should render error message", () => {
    render(<ErrorState message="Test error" />);

    expect(screen.getByText("Test error")).toBeInTheDocument();
  });

  it("should render custom title", () => {
    render(<ErrorState title="Custom Title" message="Error" />);

    expect(screen.getByText("Custom Title")).toBeInTheDocument();
  });

  it("should render retry button when onRetry is provided", async () => {
    const onRetry = jest.fn();
    render(<ErrorState message="Error" onRetry={onRetry} />);

    const retryButton = screen.getByText("Retry");
    expect(retryButton).toBeInTheDocument();

    await userEvent.click(retryButton);
    expect(onRetry).toHaveBeenCalledTimes(1);
  });

  it("should not render retry button when onRetry is not provided", () => {
    render(<ErrorState message="Error" />);

    expect(screen.queryByText("Retry")).not.toBeInTheDocument();
  });
});

