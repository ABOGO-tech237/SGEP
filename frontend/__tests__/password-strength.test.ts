// @vitest-environment node
import { describe, it, expect } from "vitest";

type StrengthLevel = "weak" | "fair" | "strong";

function getPasswordStrength(password: string): StrengthLevel | null {
  if (!password) return null;
  const hasUpper = /[A-Z]/.test(password);
  const hasLower = /[a-z]/.test(password);
  const hasDigit = /[0-9]/.test(password);
  const hasSymbol = /[^A-Za-z0-9]/.test(password);
  const types = [hasUpper, hasLower, hasDigit, hasSymbol].filter(Boolean).length;
  if (password.length < 8 || types < 2) return "weak";
  if (password.length >= 12 && types >= 3) return "strong";
  return "fair";
}

describe("getPasswordStrength", () => {
  it("returns null for empty string", () => {
    expect(getPasswordStrength("")).toBeNull();
  });

  it("returns weak for short passwords", () => {
    expect(getPasswordStrength("abc")).toBe("weak");
  });

  it("returns weak for single character type passwords", () => {
    expect(getPasswordStrength("alllower")).toBe("weak");
  });

  it("returns fair for 8+ chars with 2+ types", () => {
    expect(getPasswordStrength("Password1")).toBe("fair");
  });

  it("returns strong for 12+ chars with 3+ types", () => {
    expect(getPasswordStrength("SecurePass1!")).toBe("strong");
  });
});
