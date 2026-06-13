export interface StudentRecord {
  id: string;
  matricule: string;
  first_name: string;
  last_name: string;
  class_id?: string | null;
  academic_year_id?: string | null;
  is_active?: boolean;
  is_deleted?: boolean;
  created_at?: string;
  updated_at?: string;
  deleted_at?: string | null;
}

export interface StudentsListResponse {
  items: StudentRecord[];
  total: number;
  page: number;
  page_size: number;
}

export type AdminActivityStatus = "ACTIVE" | "SUSPENDED" | "PENDING";

export interface AdminDashboardStat {
  label: string;
  value: string;
  change: string;
  positive: boolean | null;
}

export interface AdminDashboardActivity {
  id: string;
  name: string;
  action: string;
  grade: string;
  status: AdminActivityStatus;
  time: string;
}

export interface AdminDashboardResponse {
  generated_at: string;
  stats: AdminDashboardStat[];
  recent_activity: AdminDashboardActivity[];
}