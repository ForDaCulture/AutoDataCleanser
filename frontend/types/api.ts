export interface UploadResult {
  success: boolean;
  session_id: string;
  preview: any[];
  columns: string[];
  rows: number;
}

export interface ProfileResult {
  success: boolean;
  profile: Array<{
    column: string;
    type: string;
    missing_pct: number;
    unique_count: number;
    min?: number;
    max?: number;
    mean?: number;
    std?: number;
    min_length?: number;
    max_length?: number;
    avg_length?: number;
  }>;
  preview: any[];
  rows: number;
  columns: string[];
}

export interface CleanResult {
  success: boolean;
  data: any[][];
  summary: {
    rows_processed: number;
    rows_cleaned: number;
    transformations: Array<{
      column: string;
      action: string;
      details: string;
    }>;
  };
}

export interface AuditLog {
  timestamp: string;
  action: string;
  details: string;
}

export interface ApiFeatures {
  suggestions: Array<{
    column: string;
    suggestion: string;
    confidence: number;
  }>;
}

export interface ApiError {
  detail: string;
  status: number;
} 