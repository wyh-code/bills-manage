import React from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
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

  // 未登录，跳转到登录页
  const token = authService.getToken();
  if (!token) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // 需要特定权限但用户没有，跳转到403
  if (requiredPermission && !authService.hasPermission(requiredPermission)) {
    return <Navigate to="/403" replace />;
  }

  // 渲染子组件或Outlet
  return children ? <>{children}</> : <Outlet />;
};
