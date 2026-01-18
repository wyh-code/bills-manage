import { User, AuthToken } from '@/types';

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
  wechatLogin(userInfo: { user: User, token: string }) {
    const { user, token } = userInfo;

    // 存储token
    this.setToken({ token: token, expiresIn: Date.now() + 24 * 60 * 60 * 1000 });

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
  setUser(user: User): void {
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
  setToken(token: AuthToken): void {
    this.storage.setItem(TOKEN_KEY, JSON.stringify(token));
  }

  /**
   * 获取令牌
   */
  getToken(): AuthToken | null {
    let token = null;
    const tokensStr = this.storage.getItem(TOKEN_KEY);
    if (tokensStr) {
      const tokenInfo = JSON.parse(tokensStr)
      const now = Date.now();
      if (now < tokenInfo.expiresIn) {
        token = tokenInfo.token;
      } else {
        this.clearTokens()
      }
    }
    return token;
  }

  /**
   * 清除令牌和用户信息
   */
  clearTokens(): void {
    this.storage.removeItem(TOKEN_KEY);
    this.storage.removeItem(USER_KEY);
  }

  /**
   * 检查权限
   */
  hasPermission(permission: string): boolean {
    const user = this.getUser();
    return user?.permissions.includes(permission) || false;
  }

  /**
   * 401时清除状态并跳转登录
   */
  onUnauthorized(): void {
    this.clearTokens();
    window.location.href = '/login';
  }
}

export const authService = new AuthService();
export default authService;
