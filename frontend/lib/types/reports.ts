export interface ExportJobResponse {
  job_id: string;
}

export interface ReportJobStatus {
  id: string;
  type?: string;
  status: string;
  error?: string;
  file_path?: string;
  created_at?: string;
  updated_at?: string;
}

export interface ReportCardStatus {
  id: string;
  student_id?: string;
  status: string;
  file_path?: string;
  generated_at?: string;
}
