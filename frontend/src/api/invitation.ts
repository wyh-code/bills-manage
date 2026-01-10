import apiClient from './client';

export interface CreateInvitationRequest {
  role: 'editor' | 'viewer';
}

export interface InvitationInfo {
  id: string;
  workspace_id: string;
  token: string;
  share_url: string;
  role: string;
  created_by_openid: string;
  expires_at: string;
  max_uses: number;
  used_count: number;
  status: 'active' | 'revoked';
  created_at: string;
  creator?: {
    openid: string;
    nickname: string | null;
  };
  joined_members?: Array<{
    openid: string;
    nickname: string | null;
    joined_at: string;
    is_active: boolean;
  }>;
}

export interface JoinResult {
  workspace_id: string;
  workspace_name: string;
  role: string;
  joined_at?: string;
  message?: string;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
}

class InvitationAPI {
  /**
   * 创建邀请链接
   */
  async create(workspaceId: string, data: CreateInvitationRequest): Promise<InvitationInfo> {
    const response = await apiClient.post<ApiResponse<InvitationInfo>>(
      `/workspaces/${workspaceId}/invitations`,
      data
    );

    if (!response.data.success || !response.data.data) {
      throw new Error(response.data.message || '创建邀请失败');
    }

    return response.data.data;
  }

  /**
   * 通过邀请加入空间
   */
  async join(token: string): Promise<JoinResult> {
    const response = await apiClient.post<ApiResponse<JoinResult>>(
      '/workspaces/join',
      { invitation_token: token }
    );

    if (!response.data.success || !response.data.data) {
      throw new Error(response.data.message || '加入空间失败');
    }

    return response.data.data;
  }

  /**
   * 获取邀请列表
   */
  async list(workspaceId: string, status?: 'active' | 'revoked'): Promise<InvitationInfo[]> {
    const response = await apiClient.get<ApiResponse<InvitationInfo[]>>(
      `/workspaces/${workspaceId}/invitations`,
      { params: { status } }
    );

    if (!response.data.success || !response.data.data) {
      throw new Error(response.data.message || '获取邀请列表失败');
    }

    return response.data.data;
  }

  /**
   * 撤销邀请
   */
  async revoke(workspaceId: string, invitationId: string): Promise<void> {
    const response = await apiClient.delete<ApiResponse>(
      `/workspaces/${workspaceId}/invitations/${invitationId}`
    );

    if (!response.data.success) {
      throw new Error(response.data.message || '撤销邀请失败');
    }
  }
}

export const invitationApi = new InvitationAPI();