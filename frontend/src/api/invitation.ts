import apiClient from './client';

export interface InvitationInfo {
  id: string;
  token: string;
  share_url?: string;
  type: 'platform' | 'workspace';
  workspace_id?: string;
  role?: string;
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
    agreed_at: string;
  }>;
}

export interface CreateInvitationRequest {
  type: 'platform' | 'workspace';
  workspace_id?: string;
  role?: 'editor' | 'viewer';
}

export interface JoinResult {
  type: 'platform' | 'workspace';
  user: any;
  workspace_id?: string;
  workspace_name?: string;
  role?: string;
  joined_at?: string;
  activated_at?: string;
  message?: string;
}

export interface InvitationUseRecord {
  invitation_type: 'platform' | 'workspace';
  user: {
    openid: string;
    headimgurl: string;
    nickname: string | null;
  };
  used_at: string;
  agreed_at: string;
  invitation_created_at: string;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
}

class InvitationAPI {
  /**
   * 创建邀请码
   */
  async create(data: CreateInvitationRequest): Promise<InvitationInfo> {
    const response = await apiClient.post<ApiResponse<InvitationInfo>>(
      `/invitations`,
      data
    );

    if (!response.data.success || !response.data.data) {
      throw new Error(response.data.message || '创建邀请失败');
    }

    return response.data.data;
  }

  /**
   * 通过邀请加入
   */
  async join(token: string): Promise<JoinResult> {
    const response = await apiClient.post<ApiResponse<JoinResult>>(
      '/invitations/join',
      { token }
    );

    if (!response.data.success || !response.data.data) {
      throw new Error(response.data.message || '加入失败');
    }

    return response.data.data;
  }

  /**
   * 获取邀请列表
   */
  async list(params?: { type?: string; workspace_id?: string }): Promise<InvitationInfo[]> {
    const response = await apiClient.get<ApiResponse<InvitationInfo[]>>(
      `/invitations`,
      { params }
    );

    if (!response.data.success || !response.data.data) {
      throw new Error(response.data.message || '获取邀请列表失败');
    }

    return response.data.data;
  }

  /**
   * 获取邀请使用记录
   */
  async getUses(limit?: number): Promise<InvitationUseRecord[]> {
    const response = await apiClient.get<ApiResponse<InvitationUseRecord[]>>(
      '/invitations/uses',
      { params: { limit } }
    );

    if (!response.data.success || !response.data.data) {
      throw new Error(response.data.message || '获取邀请记录失败');
    }

    return response.data.data;
  }
}

export const invitationApi = new InvitationAPI();