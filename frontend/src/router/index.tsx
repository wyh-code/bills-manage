import { createBrowserRouter, Navigate } from 'react-router-dom';
import Login from '@/pages/Login/index';
import Forbidden from '@/pages/Forbidden';
import NotFound from '@/pages/Notfound';
import { ProtectedRoute } from '@/auth/ProtectedRoute';
import Layout from '@/Layout';
import Dashboard from '@/pages/Dashboard';
import Upload from '@/pages/Upload';
import Bills from '@/pages/Bills';
import Summary from '@/pages/Summary';

export const router = createBrowserRouter([
  {
    path: '/login',
    element: <Login />,
  },
  {
    path: '/',
    element: <ProtectedRoute />,
    children: [
      {
        element: <Layout />,
        children: [
          {
            index: true,
            element: <Navigate to="/dashboard" replace />,
          },
          {
            path: 'dashboard',
            element: <Dashboard />,
          },
          {
            path: 'upload',
            element: <Upload />,
          },
          {
            path: 'bills',
            element: <Bills />,
          },
          {
            path: 'summary',
            element: <Summary />,
          },
          {
            path: '/403',
            element: <Forbidden />,
          },
          {
            path: '/404',
            element: <NotFound />,
          },
        ],
      },
    ],
  },
  {
    path: '*',
    element: <Navigate to="/404" replace />,
  },
]);
