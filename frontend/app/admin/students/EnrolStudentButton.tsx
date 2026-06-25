"use client";

import { useState } from "react";
import { UserPlus } from "lucide-react";

import { EnrolStudentModal } from "./EnrolStudentModal";

export function EnrolStudentButton() {
  const [open, setOpen] = useState(false);

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="inline-flex h-7 items-center gap-1 rounded-[min(var(--radius-md),12px)] bg-primary px-2.5 text-[0.8rem] font-medium text-primary-foreground transition hover:bg-primary/80"
      >
        <UserPlus className="size-3.5" />
        Enrol student
      </button>
      <EnrolStudentModal open={open} onOpenChange={setOpen} />
    </>
  );
}
