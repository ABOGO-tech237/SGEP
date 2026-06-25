import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { StatusBadge } from "@/components/ui/StatusBadge";

describe("StatusBadge", () => {
  it("renders the correct label for ACTIVE", () => {
    render(<StatusBadge status="ACTIVE" />);
    expect(screen.getByRole("status", { name: "Active" })).toBeInTheDocument();
  });

  it("renders the correct label for SUSPENDED", () => {
    render(<StatusBadge status="SUSPENDED" />);
    expect(screen.getByRole("status", { name: "Suspended" })).toBeInTheDocument();
  });

  it("renders the correct label for PENDING", () => {
    render(<StatusBadge status="PENDING" />);
    expect(screen.getByRole("status", { name: "Pending" })).toBeInTheDocument();
  });

  it("renders the correct label for PAID", () => {
    render(<StatusBadge status="PAID" />);
    expect(screen.getByRole("status", { name: "Paid" })).toBeInTheDocument();
  });

  it("renders the correct label for OVERDUE", () => {
    render(<StatusBadge status="OVERDUE" />);
    expect(screen.getByRole("status", { name: "Overdue" })).toBeInTheDocument();
  });

  it("applies additional className", () => {
    render(<StatusBadge status="ACTIVE" className="custom-class" />);
    expect(screen.getByRole("status")).toHaveClass("custom-class");
  });
});
