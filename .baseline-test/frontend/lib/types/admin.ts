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

export interface AdminUserSummary {
  id: string;
  email: string;
  name: string;
  first_name?: string;
  last_name?: string;
  role: string;
  account_status: string;
  created_at: string;
  updated_at?: string;
}

export interface AdminUserDashboardResponse {
  total_users: number;
  active_users: number;
  suspended_users: number;
  superadmins: number;
  comptables: number;
  parents: number;
  recent_users: AdminUserSummary[];
}

export interface AdminDashboardResponse {
  generated_at: string;
  academic_year?: { id: string; name: string } | null;
  stats: AdminDashboardStat[];
  finance?: {
    total_billed: number;
    total_collected: number;
    recovery_rate: number;
    overdue_count: number;
  };
  recent_activity: Array<{
    id: string;
    name: string;
    action: string;
    grade: string;
    status: AdminActivityStatus;
    time: string;
  }>;
  recent_users?: AdminUserSummary[];
}
