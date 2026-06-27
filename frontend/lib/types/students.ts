import { z } from "zod";

export const StudentListItemSchema = z.object({
  id: z.string(),
  matricule: z.string(),
  first_name: z.string(),
  last_name: z.string(),
  class_id: z.string().nullable().optional(),
  academic_year_id: z.string().nullable().optional(),
  is_active: z.boolean().optional(),
});

export type StudentListItem = z.infer<typeof StudentListItemSchema>;

export const StudentDetailSchema = StudentListItemSchema.extend({
  birth_date: z.string(),
  birth_place: z.string(),
  gender: z.string(),
  id_number: z.string().nullable().optional(),
  school_id: z.string().nullable().optional(),
  is_deleted: z.boolean().optional(),
  medical: z.record(z.string(), z.unknown()).nullable().optional(),
  history: z.array(z.record(z.string(), z.unknown())).optional(),
  created_at: z.string().optional(),
  updated_at: z.string().optional(),
  deleted_at: z.string().nullable().optional(),
});

export type StudentDetail = z.infer<typeof StudentDetailSchema>;

export const StudentsListResponseSchema = z.object({
  items: z.array(StudentListItemSchema),
  total: z.number(),
  page: z.number(),
  page_size: z.number(),
});

export type StudentsListResponse = z.infer<typeof StudentsListResponseSchema>;

// Edit form — class/year optional (student may not yet be enrolled)
export const CreateStudentSchema = z.object({
  first_name: z.string().min(1, "Required"),
  last_name: z.string().min(1, "Required"),
  matricule: z.string().optional(),
  birth_date: z.string().min(1, "Required"),
  birth_place: z.string().min(1, "Required"),
  gender: z.enum(["M", "F"]),
  class_id: z.string().optional(),
  academic_year_id: z.string().optional(),
  id_number: z.string().optional(),
  is_active: z.boolean().optional(),
});

export type CreateStudentFormValues = z.infer<typeof CreateStudentSchema>;

// Enroll endpoint payload — both fields required
export const EnrollStudentSchema = z.object({
  class_id: z.string().min(1, "Required"),
  academic_year_id: z.string().min(1, "Required"),
});

export type EnrollStudentFormValues = z.infer<typeof EnrollStudentSchema>;

// Registration modal — personal info + mandatory enrollment (register → enroll in one UX flow)
export const RegisterAndEnrollSchema = CreateStudentSchema.omit({
  class_id: true,
  academic_year_id: true,
}).merge(EnrollStudentSchema);

export type RegisterAndEnrollFormValues = z.infer<typeof RegisterAndEnrollSchema>;

export const StudentPromoteSchema = z.object({
  target_class_id: z.string().min(1, "Please select a target class."),
});

export type StudentPromoteValues = z.infer<typeof StudentPromoteSchema>;
