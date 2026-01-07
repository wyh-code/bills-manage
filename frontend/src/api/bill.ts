import apiClient from './client';

export interface Bill {
  id: string;
  file_upload_id: string;
  workspace_id: string;
  bank?: string;
  trade_date?: string;
  record_date?: string;
  description?: string;
  amount_cny?: number;
  card_last4?: string;
  amount_foreign?: number;
  currency?: string;
  raw_line: string;
  status: 'active' | 'inactive' | 'pending';
  created_at?: string;
}

export interface BatchConfirmRequest {
  workspace_id: string;
  file_id: string;
  bill_ids: string[];  // 要确认的账单ID列表
}

export interface BatchConfirmResponse {
  file_id: string;
  bills_count: number;
  bills: Bill[];
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
}

class BillAPI {
  /**
   * 批量确认账单（pending → active）
   */
  async batchConfirm(data: BatchConfirmRequest): Promise<BatchConfirmResponse> {
    const response = await apiClient.post<ApiResponse<BatchConfirmResponse>>(
      '/bills/batch',
      data
    );

    if (!response.data.success || !response.data.data) {
      throw new Error(response.data.message || '批量确认失败');
    }

    return response.data.data;
  }
}

export const billApi = new BillAPI();