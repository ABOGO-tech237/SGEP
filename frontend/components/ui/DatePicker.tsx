"use client";

import { useState, useRef, useEffect } from "react";
import { ChevronLeft, ChevronRight, CalendarDays } from "lucide-react";
import { cn } from "@/lib/utils";

const MONTHS = [
  "January","February","March","April","May","June",
  "July","August","September","October","November","December",
];
const DAY_LABELS = ["Su","Mo","Tu","We","Th","Fr","Sa"];

function parseISO(value: string | undefined): Date | null {
  if (!value) return null;
  const d = new Date(value + "T12:00:00");
  return isNaN(d.getTime()) ? null : d;
}

function toISO(date: Date): string {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, "0");
  const d = String(date.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

interface DatePickerProps {
  value?: string;
  onChange: (value: string) => void;
  placeholder?: string;
  id?: string;
  "aria-describedby"?: string;
  "aria-invalid"?: boolean | "true" | "false";
  className?: string;
}

export function DatePicker({
  value,
  onChange,
  placeholder = "Select a date",
  id,
  "aria-describedby": describedBy,
  "aria-invalid": ariaInvalid,
  className,
}: DatePickerProps) {
  const selected = parseISO(value);
  const today = new Date();

  const [open, setOpen] = useState(false);
  const [viewYear, setViewYear] = useState(
    selected?.getFullYear() ?? today.getFullYear(),
  );
  const [viewMonth, setViewMonth] = useState(
    selected?.getMonth() ?? today.getMonth(),
  );

  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    function onMouseDown(e: MouseEvent) {
      if (!containerRef.current?.contains(e.target as Node)) setOpen(false);
    }
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") setOpen(false);
    }
    document.addEventListener("mousedown", onMouseDown);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onMouseDown);
      document.removeEventListener("keydown", onKey);
    };
  }, [open]);

  function prevMonth() {
    if (viewMonth === 0) { setViewMonth(11); setViewYear((y) => y - 1); }
    else setViewMonth((m) => m - 1);
  }
  function nextMonth() {
    if (viewMonth === 11) { setViewMonth(0); setViewYear((y) => y + 1); }
    else setViewMonth((m) => m + 1);
  }

  function handleDayClick(day: number) {
    onChange(toISO(new Date(viewYear, viewMonth, day)));
    setOpen(false);
  }

  const daysInMonth = new Date(viewYear, viewMonth + 1, 0).getDate();
  const firstDay = new Date(viewYear, viewMonth, 1).getDay();
  const cells: (number | null)[] = [
    ...Array<null>(firstDay).fill(null),
    ...Array.from({ length: daysInMonth }, (_, i) => i + 1),
  ];
  while (cells.length % 7 !== 0) cells.push(null);

  const displayValue = selected
    ? selected.toLocaleDateString("en-GB", {
        day: "2-digit",
        month: "short",
        year: "numeric",
      })
    : "";

  const todayISO = toISO(today);

  return (
    <div ref={containerRef} className={cn("relative", className)}>
      <button
        type="button"
        id={id}
        aria-haspopup="dialog"
        aria-expanded={open}
        aria-describedby={describedBy}
        onClick={() => setOpen((v) => !v)}
        className={cn(
          "w-full flex items-center justify-between gap-2 rounded-md border border-input bg-background px-3 py-2 text-sm transition-colors",
          "ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
          ariaInvalid ? "border-destructive" : "",
          !displayValue && "text-muted-foreground",
        )}
      >
        <span>{displayValue || placeholder}</span>
        <CalendarDays className="size-4 text-muted-foreground shrink-0" />
      </button>

      {open && (
        <div
          role="dialog"
          aria-label="Date picker"
          className="absolute left-0 top-full mt-2 z-60 w-72 rounded-xl border border-border bg-card shadow-2xl"
        >
          {/* Month / year nav */}
          <div className="flex items-center justify-between px-3 py-3 border-b border-border">
            <button
              type="button"
              onClick={prevMonth}
              aria-label="Previous month"
              className="rounded-lg p-1.5 text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
            >
              <ChevronLeft className="size-4" />
            </button>

            <div className="flex items-center gap-1.5">
              <select
                value={viewMonth}
                onChange={(e) => setViewMonth(Number(e.target.value))}
                className="text-sm font-semibold bg-transparent border-none outline-none cursor-pointer hover:text-primary transition-colors"
              >
                {MONTHS.map((name, i) => (
                  <option key={name} value={i}>
                    {name}
                  </option>
                ))}
              </select>
              <input
                type="number"
                value={viewYear}
                onChange={(e) => {
                  const y = Number(e.target.value);
                  if (y > 1900 && y < 2200) setViewYear(y);
                }}
                className="w-14 text-sm font-semibold bg-transparent border-none outline-none text-center [appearance:textfield] [&::-webkit-inner-spin-button]:appearance-none [&::-webkit-outer-spin-button]:appearance-none hover:text-primary transition-colors"
              />
            </div>

            <button
              type="button"
              onClick={nextMonth}
              aria-label="Next month"
              className="rounded-lg p-1.5 text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
            >
              <ChevronRight className="size-4" />
            </button>
          </div>

          {/* Day-of-week headers */}
          <div className="grid grid-cols-7 px-3 pt-3 pb-1">
            {DAY_LABELS.map((d) => (
              <div
                key={d}
                className="text-center text-[11px] font-medium text-muted-foreground py-1 tracking-wide"
              >
                {d}
              </div>
            ))}
          </div>

          {/* Calendar grid */}
          <div className="grid grid-cols-7 px-3 pb-4 gap-y-0.5">
            {cells.map((day, i) => {
              if (!day) return <div key={i} />;
              const iso = toISO(new Date(viewYear, viewMonth, day));
              const isSelected = iso === value;
              const isToday = iso === todayISO;

              return (
                <button
                  key={i}
                  type="button"
                  onClick={() => handleDayClick(day)}
                  className={cn(
                    "mx-auto flex h-8 w-8 items-center justify-center rounded-full text-sm transition-colors",
                    isSelected
                      ? "bg-primary text-primary-foreground font-semibold shadow-sm"
                      : isToday
                        ? "ring-1 ring-primary/50 text-primary font-medium hover:bg-primary/10"
                        : "text-foreground hover:bg-muted",
                  )}
                >
                  {day}
                </button>
              );
            })}
          </div>

          {/* Today shortcut */}
          <div className="border-t border-border px-3 py-2.5 flex justify-center">
            <button
              type="button"
              onClick={() => {
                onChange(todayISO);
                setViewYear(today.getFullYear());
                setViewMonth(today.getMonth());
                setOpen(false);
              }}
              className="text-xs text-primary font-medium hover:underline transition-colors"
            >
              Today
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
