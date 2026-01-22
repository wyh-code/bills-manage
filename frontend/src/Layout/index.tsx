import { Layout as AntLayout, Menu, Button } from 'antd';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { LogoutOutlined } from '@ant-design/icons';
import authService from '@/auth/authService';
import styles from './index.module.less';

const { Header, Content } = AntLayout;

export default function Layout() {
  const navigate = useNavigate();
  const location = useLocation();
  const user = authService.getUser();

  const menuItems = [
    { key: '/dashboard', label: '工作台' },
    { key: '/upload', label: '账单上传' },
    { key: '/bills', label: '账单查询' },
    { key: '/summary', label: '账单汇总' },
  ];

  const logout = async () => {
    await authService.logout();
    navigate('/login');
  }

  return (
    <AntLayout className={styles.layout}>
      <Header className={styles.header}>
        <div className={styles.logo}>
          Amazon账单系统
        </div>
        <Menu
          mode="horizontal"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
          className={styles.menu}
        />
        <div className={styles.userActions}>
          <Button onClick={logout} style={{ border: 'none' }}>
            <LogoutOutlined />
            退出登录
          </Button>
        </div>
      </Header>
      <Content className={styles.content}>
        <Outlet />
      </Content>
    </AntLayout>
  );
}