import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { FormField } from "@/components/ui/FormField";
import type { FieldError } from "react-hook-form";

describe("FormField", () => {
  it("renders label linked to input via htmlFor/id", () => {
    render(
      <FormField label="Email" name="email">
        <input type="email" />
      </FormField>
    );
    const label = screen.getByText("Email");
    const input = screen.getByRole("textbox");
    expect(label).toHaveAttribute("for", "email");
    expect(input).toHaveAttribute("id", "email");
  });

  it("marks input as required with aria asterisk", () => {
    render(
      <FormField label="Name" name="name" required>
        <input type="text" />
      </FormField>
    );
    expect(screen.getByText("*")).toBeInTheDocument();
  });

  it("renders description text", () => {
    render(
      <FormField label="Email" name="email" description="Must be a school email">
        <input type="email" />
      </FormField>
    );
    expect(screen.getByText("Must be a school email")).toBeInTheDocument();
  });

  it("renders error message with role=alert when error is provided", () => {
    const error: FieldError = {
      type: "required",
      message: "Email is required.",
    };
    render(
      <FormField label="Email" name="email" error={error}>
        <input type="email" />
      </FormField>
    );
    const alert = screen.getByRole("alert");
    expect(alert).toHaveTextContent("Email is required.");
  });

  it("sets aria-invalid on input when there is an error", () => {
    const error: FieldError = { type: "required", message: "Required" };
    render(
      <FormField label="Email" name="email" error={error}>
        <input type="email" />
      </FormField>
    );
    expect(screen.getByRole("textbox")).toHaveAttribute("aria-invalid", "true");
  });

  it("sets aria-describedby linking input to error", () => {
    const error: FieldError = { type: "required", message: "Required" };
    render(
      <FormField label="Email" name="email" error={error}>
        <input type="email" />
      </FormField>
    );
    expect(screen.getByRole("textbox")).toHaveAttribute(
      "aria-describedby",
      "email-error"
    );
  });

  it("does not render aria-invalid when no error", () => {
    render(
      <FormField label="Email" name="email">
        <input type="email" />
      </FormField>
    );
    expect(screen.getByRole("textbox")).not.toHaveAttribute("aria-invalid");
  });
});
