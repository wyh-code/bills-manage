import React from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { getUrlParams } from '@/utils/utils';
import authService from './authService';

interface ProtectedRouteProps {
  children?: React.ReactNode;
  requiredPermission?: string;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredPermission,
}) => {
  const location = useLocation();
  const token = authService.getToken();
  const user = authService.getUser();
  const back_url = `${location.pathname}${location.search}`;

  // 未登录,跳转到登录页
  if (!token || location.pathname === '/login') {
    return <Navigate to={`/login?back_url=${encodeURIComponent(back_url)}`} state={{ from: location }} replace />;
  }

  // 用户未激活,跳转到邀请验证页
  const join = getUrlParams('join', window.location.href);
  if (user?.status === 'inactive' && !join) {
    return <Navigate to={"/invitation"} state={{ from: location }} replace />;
  }

  // 需要特定权限但用户没有,跳转到403
  if (requiredPermission && !authService.hasPermission(requiredPermission)) {
    return <Navigate to="/403" replace />;
  }

  // 渲染子组件或Outlet
  return children ? <>{children}</> : <Outlet />;
};