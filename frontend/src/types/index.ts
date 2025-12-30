export interface User {
  id: string;
  username: string;
  email: string;
  permissions: string[];
  roles: string[];
  nickname: string;
  openid: string;
  unionid: string;
  headimgurl: string;
}


export interface AuthTokens {
  token: string;
  expiresIn: number;
}

export interface LoginResponse {
  user: User;
  tokens: AuthTokens;
}

export interface RefreshResponse {
  tokens: AuthTokens;
}
