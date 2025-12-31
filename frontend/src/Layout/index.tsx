import { Layout as AntLayout, Menu, Avatar, Dropdown } from 'antd';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { UserOutlined, LogoutOutlined } from '@ant-design/icons';
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

  const userMenuItems = [
    // {
    //   key: 'logout',
    //   icon: <Avatar
    //     size={32}
    //     src={user?.headimgurl}
    //     icon={<UserOutlined />}
    //   />,
    //   label: (
    //     <div>
    //       <span className={styles.username}>
    //         {user?.nickname || user?.username || `用户${user?.id}`}
    //       </span>
    //     </div>
    //   ),
    // },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      onClick: async () => {
        await authService.logout();
        navigate('/login');
      },
    },
  ];

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
        <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
          <div className={styles.user}>
            <Avatar
              size={32}
              src={user?.headimgurl}
              icon={<UserOutlined />}
            />
          </div>
        </Dropdown>
      </Header>
      <Content className={styles.content}>
        <Outlet />
      </Content>
    </AntLayout>
  );
}
