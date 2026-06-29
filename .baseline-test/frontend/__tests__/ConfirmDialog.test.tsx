import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi } from "vitest";
import { ConfirmDialog } from "@/components/ui/ConfirmDialog";

function setup(props: Partial<Parameters<typeof ConfirmDialog>[0]> = {}) {
  const defaults = {
    open: true,
    onOpenChange: vi.fn(),
    title: "Delete record",
    description: "This action cannot be undone.",
    onConfirm: vi.fn(),
    ...props,
  };
  return { ...render(<ConfirmDialog {...defaults} />), ...defaults };
}

describe("ConfirmDialog", () => {
  it("renders title and description when open", () => {
    setup();
    expect(screen.getByText("Delete record")).toBeInTheDocument();
    expect(screen.getByText("This action cannot be undone.")).toBeInTheDocument();
  });

  it("does not render when closed", () => {
    setup({ open: false });
    expect(screen.queryByText("Delete record")).not.toBeInTheDocument();
  });

  it("calls onConfirm when confirm button is clicked", async () => {
    const user = userEvent.setup();
    const { onConfirm } = setup();
    await user.click(screen.getByRole("button", { name: "Confirm" }));
    expect(onConfirm).toHaveBeenCalledOnce();
  });

  it("calls onOpenChange(false) when cancel button is clicked", async () => {
    const user = userEvent.setup();
    const { onOpenChange } = setup();
    await user.click(screen.getByRole("button", { name: "Cancel" }));
    // @base-ui calls onOpenChange(open, event) — only assert the boolean
    expect((onOpenChange as ReturnType<typeof vi.fn>).mock.calls[0][0]).toBe(false);
  });

  it("renders custom confirmLabel and cancelLabel", () => {
    setup({ confirmLabel: "Yes, delete", cancelLabel: "Keep it" });
    expect(screen.getByRole("button", { name: "Yes, delete" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Keep it" })).toBeInTheDocument();
  });

  it("disables buttons and shows loading text when isLoading", () => {
    setup({ isLoading: true });
    const confirmBtn = screen.getByRole("button", { name: /please wait/i });
    expect(confirmBtn).toBeDisabled();
    expect(screen.getByRole("button", { name: "Cancel" })).toBeDisabled();
  });

  it("has alertdialog role for accessibility", () => {
    setup();
    expect(screen.getByRole("alertdialog")).toBeInTheDocument();
  });
});
