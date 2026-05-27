export interface AdminUserSummary {
  id: string;
  email: string;
  name: string;
  first_name: string;
  last_name: string;
  role: string;
  account_status: string;
  created_at: string;
  updated_at: string;
}

export interface AdminDashboardData {
  total_users: number;
  active_users: number;
  suspended_users: number;
  superadmins: number;
  comptables: number;
  parents: number;
  recent_users: AdminUserSummary[];
}