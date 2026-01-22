import { createBrowserRouter, Navigate } from 'react-router-dom';
import Layout from '@/Layout';
import Login from '@/pages/Login/index';
import { ProtectedRoute } from '@/auth/ProtectedRoute';
import VerifyInvitation from '@/pages/VerifyInvitation/index';
import Forbidden from '@/pages/Forbidden';
import NotFound from '@/pages/Notfound';
import Dashboard from '@/pages/Dashboard';
import Upload from '@/pages/Upload';
import Bills from '@/pages/Bills';
import Summary from '@/pages/Summary';
import Usercenter from '@/pages/Usercenter';
import Usage from '@/pages/Usercenter/Usage';
import Topup from '@/pages/Usercenter/Topup';
import Transactions from '@/pages/Usercenter/Transactions';

export const router = createBrowserRouter([
  {
    path: '/login',
    element: <Login />,
  },
  {
    path: '/invitation',
    element: <VerifyInvitation />,
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
            path: 'usercenter',
            element: <Usercenter />,
            children: [
              {
                index: true,
                element: <Navigate to="/usercenter/usage" replace />,
              },
              {
                path: 'usage',
                element: <Usage />,
              },
              {
                path: 'topup',
                element: <Topup />,
              },
              {
                path: 'transactions',
                element: <Transactions />,
              }
            ]
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