import { User, AuthTokens } from '@/types';

const TOKEN_KEY = 'auth_tokens';
const USER_KEY = 'auth_user';

class AuthService {
  private storage: Storage;

  constructor() {
    this.storage = window.localStorage;
  }

  /**
   * 微信登录（存储token和用户信息）
   */
  wechatLogin(userInfo: { user:User, token: string }) {

    const { user, token } = userInfo;

    // 存储token
    this.setToken({
      token,
      expiresIn: 7200,
    });

    // 存储用户信息
    this.setUser(user);
  }

  /**
   * 登出
   */
  async logout(): Promise<void> {
    this.clearTokens();
  }

  /**
   * 设置用户信息
   */
  private setUser(user: User): void {
    this.storage.setItem(USER_KEY, JSON.stringify(user));
  }

  /**
   * 获取当前用户
   */
  getUser(): User | null {
    const userStr = this.storage.getItem(USER_KEY);
    return userStr ? JSON.parse(userStr) : null;
  }

  /**
   * 设置令牌
   */
  setToken(token: AuthTokens): void {
    this.storage.setItem(TOKEN_KEY, JSON.stringify(token));
  }

  /**
   * 获取令牌
   */
  getToken(): AuthTokens | null {
    const tokensStr = this.storage.getItem(TOKEN_KEY);
    return tokensStr ? JSON.parse(tokensStr) : null;
  }

  /**
   * 检查权限
   */
  hasPermission(permission: string): boolean {
    const user = this.getUser();
    return user?.permissions.includes(permission) || false;
  }

  /**
   * 清除令牌和用户信息
   */
  clearTokens(): void {
    this.storage.removeItem(TOKEN_KEY);
    this.storage.removeItem(USER_KEY);
  }

  /**
   * 清除令牌和用户信息
   * 跳转登录页
   */
  onUnauthorized():void  {
    this.clearTokens();
    // 401时清除状态并跳转登录
    window.location.href = '/login';
  }
}

export const authService = new AuthService();
export default authService;
