import { z } from "zod";

export interface SchoolRecord {
  id: string;
  name: string;
  code: string;
  address?: string;
  phone?: string;
  email?: string;
  is_active?: boolean;
}

export interface AcademicYearRecord {
  id: string;
  name: string;
  start_date: string;
  end_date: string;
  school_id?: string;
  is_active?: boolean;
}

export const SchoolCreateSchema = z.object({
  name: z.string().min(1, "Name is required."),
  code: z.string().min(1, "Code is required."),
  address: z.string().optional(),
  phone: z.string().optional(),
  email: z.string().email().optional().or(z.literal("")),
  is_active: z.boolean().optional(),
});

export type SchoolCreateValues = z.infer<typeof SchoolCreateSchema>;

export const AcademicYearCreateSchema = z.object({
  name: z.string().min(1, "Name is required."),
  start_date: z.string().min(1, "Start date is required."),
  end_date: z.string().min(1, "End date is required."),
  school_id: z.string().optional(),
  is_active: z.boolean().optional(),
});

export type AcademicYearCreateValues = z.infer<typeof AcademicYearCreateSchema>;
