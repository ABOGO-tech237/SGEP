"use client";

import { cloneElement, isValidElement } from "react";
import { cn } from "@/lib/utils";
import type { FieldError } from "react-hook-form";

interface FormFieldProps {
  label: string;
  name: string;
  error?: FieldError;
  required?: boolean;
  description?: string;
  children: React.ReactElement;
  className?: string;
}

export function FormField({
  label,
  name,
  error,
  required,
  description,
  children,
  className,
}: FormFieldProps) {
  const descId = `${name}-desc`;
  const errId = `${name}-error`;
  const describedBy = [
    description ? descId : null,
    error ? errId : null,
  ]
    .filter(Boolean)
    .join(" ") || undefined;

  const input = isValidElement(children)
    ? cloneElement(children as React.ReactElement<Record<string, unknown>>, {
        id: name,
        "aria-describedby": describedBy,
        "aria-invalid": error ? true : undefined,
      })
    : children;

  return (
    <div className={cn("flex flex-col gap-1.5", className)}>
      <label htmlFor={name} className="text-sm font-medium">
        {label}
        {required && (
          <span aria-hidden className="ml-0.5 text-destructive">
            *
          </span>
        )}
      </label>
      {input}
      {description && (
        <p id={descId} className="text-xs text-muted-foreground">
          {description}
        </p>
      )}
      {error?.message && (
        <p id={errId} role="alert" className="text-xs text-destructive">
          {error.message}
        </p>
      )}
    </div>
  );
}
