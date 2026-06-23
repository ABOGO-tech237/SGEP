import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { PdfDownload } from "@/components/ui/PdfDownload";

function mockFetch(ok: boolean) {
  const blob = new Blob(["PDF content"], { type: "application/pdf" });
  return vi.spyOn(globalThis, "fetch").mockResolvedValue({
    ok,
    status: ok ? 200 : 500,
    blob: () => Promise.resolve(blob),
  } as Response);
}

describe("PdfDownload", () => {
  let createObjectURL: ReturnType<typeof vi.fn>;
  let revokeObjectURL: ReturnType<typeof vi.fn>;
  let clickSpy: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    createObjectURL = vi.fn().mockReturnValue("blob:mock-url");
    revokeObjectURL = vi.fn();
    URL.createObjectURL = createObjectURL as unknown as typeof URL.createObjectURL;
    URL.revokeObjectURL = revokeObjectURL as unknown as typeof URL.revokeObjectURL;
    clickSpy = vi.fn();
    const originalCreateElement = document.createElement.bind(document);
    vi.spyOn(document, "createElement").mockImplementation((tag: string) => {
      if (tag === "a") {
        const anchor = { href: "", download: "", click: clickSpy } as unknown as HTMLAnchorElement;
        return anchor;
      }
      return originalCreateElement(tag);
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("renders the download button with default label", () => {
    render(<PdfDownload href="/api/reports/fees" />);
    expect(screen.getByRole("button", { name: /download pdf/i })).toBeInTheDocument();
  });

  it("renders custom label", () => {
    render(<PdfDownload href="/api/reports/fees" label="Get receipt" />);
    expect(screen.getByRole("button", { name: /get receipt/i })).toBeInTheDocument();
  });

  it("fetches and triggers download on click", async () => {
    const user = userEvent.setup();
    mockFetch(true);
    render(<PdfDownload href="/api/reports/fees" filename="fees.pdf" />);
    await user.click(screen.getByRole("button", { name: /download pdf/i }));
    await waitFor(() => expect(createObjectURL).toHaveBeenCalled());
    expect(clickSpy).toHaveBeenCalled();
    expect(revokeObjectURL).toHaveBeenCalledWith("blob:mock-url");
  });

  it("appends query params to the URL when params are provided", async () => {
    const user = userEvent.setup();
    const fetchSpy = mockFetch(true);
    render(<PdfDownload href="/api/reports/fees" params={{ term: "2025-1" }} />);
    await user.click(screen.getByRole("button", { name: /download pdf/i }));
    await waitFor(() =>
      expect(fetchSpy).toHaveBeenCalledWith("/api/reports/fees?term=2025-1")
    );
  });

  it("shows error message when fetch fails", async () => {
    const user = userEvent.setup();
    mockFetch(false);
    render(<PdfDownload href="/api/reports/fees" />);
    await user.click(screen.getByRole("button", { name: /download pdf/i }));
    await waitFor(() =>
      expect(screen.getByRole("alert")).toHaveTextContent(/download failed/i)
    );
  });

  it("sets aria-busy during download", async () => {
    const user = userEvent.setup();
    let resolveBlob!: (b: Blob) => void;
    const blob = new Blob(["PDF"], { type: "application/pdf" });
    vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
      blob: () => new Promise<Blob>((res) => { resolveBlob = res; }),
    } as Response);
    render(<PdfDownload href="/api/reports/fees" />);
    const btn = screen.getByRole("button", { name: /download pdf/i });
    await user.click(btn);
    expect(btn).toHaveAttribute("aria-busy", "true");
    resolveBlob(blob);
    await waitFor(() => expect(btn).toHaveAttribute("aria-busy", "false"));
  });
});
