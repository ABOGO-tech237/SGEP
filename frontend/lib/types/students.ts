import { z } from "zod";

export interface StudentListItem {
  id: string;
  matricule: string;
  first_name: string;
  last_name: string;
  class_id?: string | null;
  academic_year_id?: string | null;
  is_active?: boolean;
}

export interface StudentDetail extends StudentListItem {
  birth_date: string;
  birth_place: string;
  gender: string;
  id_number?: string | null;
  school_id?: string | null;
  is_deleted?: boolean;
  medical?: Record<string, unknown> | null;
  history?: Array<Record<string, unknown>>;
  created_at?: string;
  updated_at?: string;
  deleted_at?: string | null;
}

export interface StudentsListResponse {
  items: StudentListItem[];
  total: number;
  page: number;
  page_size: number;
}

export const StudentCreateSchema = z.object({
  first_name: z.string().min(1, "First name is required."),
  last_name: z.string().min(1, "Last name is required."),
  matricule: z.string().optional(),
  birth_date: z.string().min(1, "Birth date is required."),
  birth_place: z.string().min(1, "Birth place is required."),
  gender: z.string().min(1, "Gender is required."),
  id_number: z.string().optional(),
  class_id: z.string().min(1, "Class is required."),
  academic_year_id: z.string().min(1, "Academic year is required."),
  school_id: z.string().optional(),
  is_active: z.boolean().optional(),
});

export type StudentCreateValues = z.infer<typeof StudentCreateSchema>;

export const StudentEnrollSchema = z.object({
  class_id: z.string().min(1, "Class is required."),
  academic_year_id: z.string().min(1, "Academic year is required."),
});

export type StudentEnrollValues = z.infer<typeof StudentEnrollSchema>;

export const StudentPromoteSchema = z.object({
  target_class_id: z.string().min(1, "Target class is required."),
});

export type StudentPromoteValues = z.infer<typeof StudentPromoteSchema>;
