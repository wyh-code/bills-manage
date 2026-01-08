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

export interface BillListParams {
  workspace_ids?: string[];  // 空间ID列表（多选）
  card_last4_list?: string[];  // 卡号列表（多选）
  start_date?: string;  // YYYY-MM-DD
  end_date?: string;    // YYYY-MM-DD
  page?: number;
  page_size?: number;
}

export interface BillListResponse {
  total: number;
  page: number;
  page_size: number;
  items: Bill[];
}

export interface CardOption {
  card_last4: string;
  count: number;
}

export interface BatchConfirmRequest {
  workspace_id: string;
  file_id: string;
  bill_ids: string[];
}

export interface BatchConfirmResponse {
  file_id: string;
  bills_count: number;
  updated_count: number;
  bills: Bill[];
}

export interface BatchUpdateItem {
  bill_id: string;
  data: Bill[];
}

export interface BatchUpdateRequest {
  workspace_id: string;
  updates: BatchUpdateItem[];
}

export interface BatchUpdateResponse {
  updated_count: number;
  failed_count: number;
  results: Array<{
    bill_id: string;
    success: boolean;
    message?: string;
  }>;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
}

class BillAPI {
  /**
   * 分页查询账单列表
   */
  async list(params: BillListParams): Promise<BillListResponse> {
    // 转换数组参数为逗号分隔字符串
    const queryParams: any = {
      ...params,
      workspace_ids: params.workspace_ids?.join(','),
      card_last4_list: params.card_last4_list?.join(','),
      page: params.page || 1,
      page_size: params.page_size || 20,
    };

    const response = await apiClient.get<ApiResponse<BillListResponse>>(
      '/bills',
      { params: queryParams }
    );

    if (!response.data.success || !response.data.data) {
      throw new Error(response.data.message || '获取账单列表失败');
    }

    return response.data.data;
  }

  /**
   * 获取卡号列表（用于筛选下拉）
   */
  async getCardList(workspaceIds?: string[]): Promise<CardOption[]> {
    const params: any = {};
    if (workspaceIds && workspaceIds.length > 0) {
      params.workspace_ids = workspaceIds.join(',');
    }

    const response = await apiClient.get<ApiResponse<CardOption[]>>(
      '/bills/cards',
      { params }
    );

    if (!response.data.success || !response.data.data) {
      throw new Error(response.data.message || '获取卡号列表失败');
    }

    return response.data.data;
  }

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

  /**
   * 获取单个账单详情
   */
  async get(workspaceId: string, billId: string): Promise<Bill> {
    const response = await apiClient.get<ApiResponse<Bill>>(
      `/bills/${billId}`,
      { params: { workspace_id: workspaceId } }
    );

    if (!response.data.success || !response.data.data) {
      throw new Error(response.data.message || '获取账单详情失败');
    }

    return response.data.data;
  }

  /**
   * 更新账单
   */
  async update(workspaceId: string, billId: string, data: Partial<Bill>): Promise<Bill> {
    const response = await apiClient.put<ApiResponse<Bill>>(
      `/bills/${billId}`,
      data,
      { params: { workspace_id: workspaceId } }
    );

    if (!response.data.success || !response.data.data) {
      throw new Error(response.data.message || '更新账单失败');
    }

    return response.data.data;
  }

  /**
   * 批量更新账单
   */
  async batchUpdate(data: BatchUpdateRequest): Promise<BatchUpdateResponse> {
    const response = await apiClient.put<ApiResponse<BatchUpdateResponse>>(
      '/bills/update',
      data
    );

    if (!response.data.success || !response.data.data) {
      throw new Error(response.data.message || '批量更新失败');
    }

    return response.data.data;
  }

  /**
   * 删除账单
   */
  async delete(workspaceId: string, billId: string): Promise<void> {
    const response = await apiClient.delete<ApiResponse>(
      `/bills/${billId}`,
      { params: { workspace_id: workspaceId } }
    );

    if (!response.data.success) {
      throw new Error(response.data.message || '删除账单失败');
    }
  }
}

export const billApi = new BillAPI();