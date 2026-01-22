import apiClient from './client';

interface PaginationParams {
  page?: number;
  page_size?: number;
}

class AccountAPI {
  /**
   * 查询账户余额
   */
  async balance() {
    const response = await apiClient.get('/accounts/balance');

    if (!response.data.success || !response.data.data) {
      throw new Error(response.data.message || '查询账户余额失败');
    }

    return response.data.data;
  }
  /**
   * 查询每月消耗账户余额
   */
  async usageMonthly(month: string) {
    const response = await apiClient.get('/accounts/usage/monthly', { params: { month } });

    if (!response.data.success || !response.data.data) {
      throw new Error(response.data.message || '查询账户余额失败');
    }

    return response.data.data;
  }
  /**
   * 导出消耗汇总
   */
  async export(month: string) {
    const response = await apiClient.get('/accounts/usage/export', {
      params: { month },
      responseType: 'blob',
    });

    // 从响应头提取文件名
    const disposition = response.headers['content-disposition'];
    let filename = `用量报表_${month}.xlsx`;

    if (disposition) {
      const filenameMatch = disposition.match(/filename\*?=["']?(?:UTF-8'')?([^"';]+)["']?/i);
      if (filenameMatch) {
        filename = decodeURIComponent(filenameMatch[1]);
      }
    }

    // 创建 Blob 并触发下载
    const blob = new Blob([response.data]);
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    return true;
  }

  /**
  * 获取扣费记录
  */
  async getBillingRecords(params: PaginationParams = {}) {
    const response = await apiClient.get('/accounts/billing/records', { params });

    if (!response.data.success) {
      throw new Error(response.data.message || '获取扣费记录失败');
    }

    return response.data.data;
  }
}



export const accountApi = new AccountAPI();
