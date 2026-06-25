// @vitest-environment node
import { describe, it, expect } from "vitest";
import { LoginSchema } from "../lib/types/auth";

describe("LoginSchema", () => {
  it("accepts valid credentials", () => {
    const result = LoginSchema.safeParse({
      email: "admin@school.cm",
      password: "S3cur3P@ss!",
    });
    expect(result.success).toBe(true);
  });

  it("rejects an invalid email", () => {
    const result = LoginSchema.safeParse({
      email: "not-an-email",
      password: "anything",
    });
    expect(result.success).toBe(false);
    const issues = result.error!.issues;
    expect(issues.some((i) => i.path[0] === "email")).toBe(true);
  });

  it("rejects an empty password", () => {
    const result = LoginSchema.safeParse({
      email: "admin@school.cm",
      password: "",
    });
    expect(result.success).toBe(false);
    const issues = result.error!.issues;
    expect(issues.some((i) => i.path[0] === "password")).toBe(true);
  });

  it("rejects a missing email", () => {
    const result = LoginSchema.safeParse({ password: "secret" });
    expect(result.success).toBe(false);
  });

  it("does not enumerate user existence in error messages", () => {
    // Schema errors must not mention whether the account exists
    const result = LoginSchema.safeParse({ email: "bad", password: "" });
    const messages = result.error!.issues.map((i) => i.message.toLowerCase());
    expect(messages.every((m) => !m.includes("account"))).toBe(true);
    expect(messages.every((m) => !m.includes("exist"))).toBe(true);
    expect(messages.every((m) => !m.includes("found"))).toBe(true);
  });
});
