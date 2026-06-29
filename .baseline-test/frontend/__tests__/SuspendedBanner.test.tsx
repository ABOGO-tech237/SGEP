import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { SuspendedBanner } from "@/components/ui/SuspendedBanner";

describe("SuspendedBanner", () => {
  it("renders children normally when not suspended", () => {
    render(
      <SuspendedBanner isSuspended={false}>
        <button>Pay fees</button>
      </SuspendedBanner>
    );
    expect(screen.getByRole("button", { name: "Pay fees" })).toBeInTheDocument();
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });

  it("shows suspension alert when isSuspended is true", () => {
    render(
      <SuspendedBanner isSuspended={true}>
        <button>Pay fees</button>
      </SuspendedBanner>
    );
    expect(screen.getByRole("alert")).toBeInTheDocument();
    expect(screen.getByText("Account suspended")).toBeInTheDocument();
  });

  it("shows custom reason when provided", () => {
    render(
      <SuspendedBanner isSuspended={true} reason="Outstanding balance of 50,000 FCFA">
        <div>content</div>
      </SuspendedBanner>
    );
    expect(
      screen.getByText("Outstanding balance of 50,000 FCFA")
    ).toBeInTheDocument();
  });

  it("blocks interaction with children via inert attribute", () => {
    const { container } = render(
      <SuspendedBanner isSuspended={true}>
        <button>Pay fees</button>
      </SuspendedBanner>
    );
    // inert removes elements from the a11y tree; use DOM query
    const inertWrapper = container.querySelector("[inert]");
    expect(inertWrapper).toBeInTheDocument();
    expect(inertWrapper?.querySelector("button")).toBeInTheDocument();
  });

  it("includes admin contact message", () => {
    render(
      <SuspendedBanner isSuspended={true}>
        <div />
      </SuspendedBanner>
    );
    expect(
      screen.getByText(/contact the school administration/i)
    ).toBeInTheDocument();
  });
});
