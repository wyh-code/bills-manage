import apiClient from './client';

export interface UploadFileResponse {
  status: 'success' | 'duplicate';
  data: {
    file_id: string;
    original_filename: string;
    file_size: number;
    raw_content?: string;
    upload_time?: number;
    bills?: any[];
    bills_count?: number;
  };
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  status?: string;
}

class FileAPI {
  /**
   * 上传文件并解析
   */
  async upload(workspaceId: string, file: File): Promise<UploadFileResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post<ApiResponse<UploadFileResponse['data']>>(
      `/files/upload`,
      formData,
      {
        params: { workspace_id: workspaceId },
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );

    if (!response.data.success || !response.data.data) {
      throw new Error(response.data.message || '文件上传失败');
    }

    return {
      status: response.data.status as 'success' | 'duplicate',
      data: response.data.data,
    };
  }

  /**
   * 获取文件处理进度
   */
  async getProgress(fileId: string, workspaceId: string): Promise<{
    file_id: string;
    original_filename: string;
    file_status: 'processing' | 'completed' | 'failed';
    bills_count: number;
    bills?: any;
  }> {
    const response = await apiClient.get(
      `/files/${fileId}/progress`,
      {
        params: { workspace_id: workspaceId },
      }
    );

    if (!response.data.success || !response.data.data) {
      throw new Error(response.data.message || '获取进度失败');
    }

    return response.data.data;
  }
}

export const fileApi = new FileAPI();