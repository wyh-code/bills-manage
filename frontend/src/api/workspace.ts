import apiClient from './client';

export interface Workspace {
  id: string;
  name: string;
  description: string | null;
  owner_openid: string;
  created_at: string;
  updated_at: string;
  status: string;
  owner: any;
  members: any;
  user_role?: 'owner' | 'editor' | 'viewer';  // 用户在该空间的角色
}

export interface CreateWorkspaceRequest {
  name: string;
  description?: string;
}

export interface UpdateWorkspaceRequest {
  name?: string;
  description?: string;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
}

class WorkspaceAPI {
  /**
   * 创建空间
   */
  async create(data: CreateWorkspaceRequest): Promise<Workspace> {
    const response = await apiClient.post<ApiResponse<Workspace>>(
      '/workspaces',
      data
    );
    
    if (!response.data.success || !response.data.data) {
      throw new Error(response.data.message || '创建空间失败');
    }
    
    return response.data.data;
  }

  /**
   * 获取用户所有空间列表
   */
  async list(params?: { status: string, role: string }): Promise<Workspace[]> {
    const response = await apiClient.get<ApiResponse<Workspace[]>>(
      '/workspaces', { params }
    );
    
    if (!response.data.success || !response.data.data) {
      throw new Error(response.data.message || '获取空间列表失败');
    }
    
    return response.data.data;
  }

  /**
   * 获取空间详情
   */
  async get(workspaceId: number): Promise<Workspace> {
    const response = await apiClient.get<ApiResponse<Workspace>>(
      `/workspaces/${workspaceId}`
    );
    
    if (!response.data.success || !response.data.data) {
      throw new Error(response.data.message || '获取空间详情失败');
    }
    
    return response.data.data;
  }

  /**
   * 更新空间
   */
  async update(workspaceId: number, data: UpdateWorkspaceRequest): Promise<Workspace> {
    const response = await apiClient.put<ApiResponse<Workspace>>(
      `/workspaces/${workspaceId}`,
      data
    );
    
    if (!response.data.success || !response.data.data) {
      throw new Error(response.data.message || '更新空间失败');
    }
    
    return response.data.data;
  }

  /**
   * 删除空间
   */
  async delete(workspaceId: number): Promise<void> {
    const response = await apiClient.delete<ApiResponse>(
      `/workspaces/${workspaceId}`
    );
    
    if (!response.data.success) {
      throw new Error(response.data.message || '删除空间失败');
    }
  }
}

export const workspaceApi = new WorkspaceAPI();
