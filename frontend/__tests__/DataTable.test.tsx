import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi } from "vitest";
import { DataTable } from "@/components/ui/DataTable";
import type { ColumnDef } from "@tanstack/react-table";

interface Person {
  name: string;
  role: string;
  age: number;
}

const columns: ColumnDef<Person>[] = [
  { accessorKey: "name", header: "Name" },
  { accessorKey: "role", header: "Role" },
  { accessorKey: "age", header: "Age" },
];

const data: Person[] = [
  { name: "Alice", role: "Admin", age: 30 },
  { name: "Bob", role: "Parent", age: 45 },
  { name: "Carol", role: "Accountant", age: 28 },
];

describe("DataTable", () => {
  it("renders column headers", () => {
    render(<DataTable data={data} columns={columns} />);
    expect(screen.getByRole("columnheader", { name: "Name" })).toBeInTheDocument();
    expect(screen.getByRole("columnheader", { name: "Role" })).toBeInTheDocument();
    expect(screen.getByRole("columnheader", { name: "Age" })).toBeInTheDocument();
  });

  it("renders all data rows", () => {
    render(<DataTable data={data} columns={columns} />);
    expect(screen.getByText("Alice")).toBeInTheDocument();
    expect(screen.getByText("Bob")).toBeInTheDocument();
    expect(screen.getByText("Carol")).toBeInTheDocument();
  });

  it("filters rows by global filter", async () => {
    const user = userEvent.setup();
    render(<DataTable data={data} columns={columns} />);
    const input = screen.getByRole("searchbox");
    await user.type(input, "Alice");
    expect(screen.getByText("Alice")).toBeInTheDocument();
    expect(screen.queryByText("Bob")).not.toBeInTheDocument();
  });

  it("shows empty state message when no results match filter", async () => {
    const user = userEvent.setup();
    render(<DataTable data={data} columns={columns} />);
    await user.type(screen.getByRole("searchbox"), "zzz-no-match");
    expect(screen.getByText("No results found.")).toBeInTheDocument();
  });

  it("sorts column ascending/descending on header click", async () => {
    const user = userEvent.setup();
    render(<DataTable data={data} columns={columns} />);
    const nameHeader = screen.getByRole("columnheader", { name: /name/i });
    await user.click(nameHeader);
    expect(nameHeader).toHaveAttribute("aria-sort", "ascending");
    await user.click(nameHeader);
    expect(nameHeader).toHaveAttribute("aria-sort", "descending");
  });

  it("renders pagination controls when data exceeds pageSize", () => {
    const manyRows = Array.from({ length: 15 }, (_, i) => ({
      name: `Person ${i}`,
      role: "Parent",
      age: 30 + i,
    }));
    render(<DataTable data={manyRows} columns={columns} pageSize={5} />);
    expect(screen.getByRole("navigation", { name: "Pagination" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Next page" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Previous page" })).toBeInTheDocument();
  });

  it("does not show pagination when all rows fit on one page", () => {
    render(<DataTable data={data} columns={columns} pageSize={10} />);
    expect(screen.queryByRole("navigation", { name: "Pagination" })).not.toBeInTheDocument();
  });

  it("navigates to next page", async () => {
    const user = userEvent.setup();
    const manyRows = Array.from({ length: 6 }, (_, i) => ({
      name: `Person ${i}`,
      role: "Parent",
      age: 30 + i,
    }));
    render(<DataTable data={manyRows} columns={columns} pageSize={5} />);
    expect(screen.getByText("Page 1 of 2")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Next page" }));
    expect(screen.getByText("Page 2 of 2")).toBeInTheDocument();
  });

  it("renders export button", () => {
    render(<DataTable data={data} columns={columns} />);
    expect(screen.getByRole("button", { name: "Export to CSV" })).toBeInTheDocument();
  });

  it("triggers CSV download on export click", async () => {
    const user = userEvent.setup();
    const createObjectURL = vi.fn().mockReturnValue("blob:mock");
    const revokeObjectURL = vi.fn();
    const clickSpy = vi.fn();
    URL.createObjectURL = createObjectURL;
    URL.revokeObjectURL = revokeObjectURL;
    const originalCreateElement = document.createElement.bind(document);
    vi.spyOn(document, "createElement").mockImplementation((tag: string) => {
      if (tag === "a") {
        return { href: "", download: "", click: clickSpy } as unknown as HTMLAnchorElement;
      }
      return originalCreateElement(tag);
    });

    render(<DataTable data={data} columns={columns} exportFilename="test.csv" />);
    await user.click(screen.getByRole("button", { name: "Export to CSV" }));
    expect(createObjectURL).toHaveBeenCalled();
    expect(clickSpy).toHaveBeenCalled();

    vi.restoreAllMocks();
  });
});
