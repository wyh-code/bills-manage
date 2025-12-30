
export interface User {
  id: string;
  username: string;
  email: string;
  permissions: string[];
  roles?: string[];
  nickname: string;
  openid?: string;
  unionid?: string;
  headimgurl: string;
}


export interface AuthToken {
  token: string;
  expiresIn: number;
}

export interface LoginResponse {
  user: User;
  token: AuthToken;
}

export interface RefreshResponse {
  token: AuthToken;
}
