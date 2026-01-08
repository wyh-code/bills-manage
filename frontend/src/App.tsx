import { RouterProvider } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import dayjs from 'dayjs';
import 'dayjs/locale/zh-cn';
import zhCN from 'antd/locale/zh_CN';
import { router } from './router';
import './global.less';

dayjs.locale('zh-cn');

export default function App() {

  return (
    <ConfigProvider
      locale={zhCN}
      theme={{
        token: {
          // Seed Token，影响范围大
          colorPrimary: '#FF6619',
          borderRadius: 4,
          colorTextBase: '#111720',
          colorTextPlaceholder: '#bcc5d1',
          colorErrorOutline: '#F04631',
        },
      }}
    >
      <RouterProvider router={router} />
    </ConfigProvider>
  );
}
