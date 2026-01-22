import authService from '@/auth/authService';
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

export interface FileInfo {
  remark: string;
  file_id: string;
  original_filename: string;
  file_status: 'processing' | 'completed' | 'failed';
  bills_count: number;
  bills?: any[];
}

export interface FileRecord {
  file_id: string;
  file_name: string;
  workspace_id: string;
  uploader: {
    openid: string;
    nickname: string | null;
  };
  upload_time: string;
  bills_count: number;
  total_amount: Record<string, number>;
  bills: any[];
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
  async getProgress(fileId: string, workspaceId: string): Promise<FileInfo> {
    const response = await apiClient.get<ApiResponse<FileInfo>>(
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

  /**
   * 获取文件预览 URL（用于 PDF/图片直接预览）
   * * @param fileId 文件ID
   * @param workspaceId 空间ID
   * @returns 可直接用于预览的URL（包含token）
   */
  getPreviewUrl(fileId: string, workspaceId: string): string {
    const token = authService.getToken();
    const baseUrl = apiClient.defaults.baseURL;
    return `${baseUrl}/files/${fileId}?workspace_id=${workspaceId}&token=${token}`;
  }

  /**
   * 获取文件下载 URL
   * @param fileId 文件ID
   * @param workspaceId 空间ID
   * @returns 可直接用于下载的URL（包含token）
   */
  getDownloadUrl(fileId: string, workspaceId: string): string {
    const token = authService.getToken();
    const baseUrl = apiClient.defaults.baseURL;
    return `${baseUrl}/files/${fileId}?workspace_id=${workspaceId}&download=true&token=${token}`;
  }

  /**
   * 获取文件用于预览（转换为 File 对象）
   */
  async getFileForPreview(fileId: string, workspaceId: string): Promise<File> {
    try {
      // 获取文件信息（含文件名）
      const fileInfo = await this.getProgress(fileId, workspaceId);

      // 下载文件
      const response = await apiClient.get(`/files/${fileId}`, {
        params: { workspace_id: workspaceId },
        responseType: 'blob',
      });

      // 转换为 File 对象
      const file = new File([response.data], fileInfo.original_filename, {
        type: response.headers['content-type'] || 'application/octet-stream',
      });

      return file;
    } catch (error) {
      throw new Error('获取文件失败');
    }
  }

  /**
   * 预览文件（新标签页打开，适用于 PDF/图片）
   */
  preview(fileId: string, workspaceId: string): void {
    const url = this.getPreviewUrl(fileId, workspaceId);
    window.open(url, '_blank');
  }

  /**
   * 下载文件
   */
  async download(fileId: string, workspaceId: string): Promise<void> {
    try {
      const fileInfo = await this.getProgress(fileId, workspaceId);

      const response = await apiClient.get(`/files/${fileId}`, {
        params: {
          workspace_id: workspaceId,
          download: true,
        },
        responseType: 'blob',
      });

      // 从响应头提取文件名
      const disposition = response.headers['content-disposition'];
      let filename = fileInfo.original_filename;

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
    } catch (error) {
      throw new Error('文件下载失败');
    }
  }

  /**
   * 获取文件上传记录
   */
  async getRecords(params): Promise<any> {
    const response = await apiClient.get<ApiResponse<any>>(
      '/files/records',
      { params }
    );

    if (!response.data.success || !response.data.data) {
      throw new Error(response.data.message || '获取文件记录失败');
    }

    return response.data;
  }
}

export const fileApi = new FileAPI();