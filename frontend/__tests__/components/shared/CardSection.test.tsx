/**
 * @jest-environment jsdom
 */

import { render, screen } from "@testing-library/react";
import { CardSection } from "@/components/shared/CardSection";

describe("CardSection", () => {
  it("should render children", () => {
    render(
      <CardSection>
        <div>Test Content</div>
      </CardSection>
    );

    expect(screen.getByText("Test Content")).toBeInTheDocument();
  });

  it("should render title when provided", () => {
    render(<CardSection title="Test Title">Content</CardSection>);

    expect(screen.getByText("Test Title")).toBeInTheDocument();
  });

  it("should render header actions when provided", () => {
    render(
      <CardSection
        title="Test"
        headerActions={<button>Action</button>}
      >
        Content
      </CardSection>
    );

    expect(screen.getByText("Action")).toBeInTheDocument();
  });

  it("should apply custom className", () => {
    const { container } = render(
      <CardSection className="custom-class">Content</CardSection>
    );

    expect(container.firstChild).toHaveClass("custom-class");
  });
});

