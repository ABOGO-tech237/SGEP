"use client";

import { useState } from "react";
import { UserPlus } from "lucide-react";
import { EnrolStudentModal } from "./EnrolStudentModal";

export function EnrolStudentButton() {
  const [open, setOpen] = useState(false);

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        className="inline-flex items-center gap-1.5 rounded-md bg-primary px-3 py-1.5 text-sm font-semibold text-primary-foreground transition hover:bg-primary/90"
      >
        <UserPlus className="size-3.5" />
        Enrol student
      </button>
      <EnrolStudentModal open={open} onOpenChange={setOpen} />
    </>
  );
}
