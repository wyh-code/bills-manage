import { RouterProvider } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import { router } from './router';
import './global.css';

export default function App() {

  return (
    <ConfigProvider
      locale={zhCN}
      theme={{
        token: {
          // Seed Token，影响范围大
          colorPrimary: '#FF6619',
          borderRadius: 8,
        },
      }}
    >
      <RouterProvider router={router} />
    </ConfigProvider>
  );
}
