import { Menu } from 'antd';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  DashboardOutlined,
  CreditCardOutlined,
  ContainerOutlined
} from '@ant-design/icons';
import styles from './index.module.less';


export default () => {
  const navigate = useNavigate();
  const location = useLocation();

  // 处理菜单点击
  const handleMenuClick = (key) => {
    switch (key) {
      case 'usage':
        navigate('/usercenter/usage');
        break;
      case 'topup':
        navigate('/usercenter/topup');
        break;
      case 'transactions':
        navigate('/usercenter/transactions');
        break;
      default:
        break;
    }
  };

  // 根据当前路径设置选中的菜单项
  const getSelectedKey = () => {
    const path = location.pathname;
    if (path.includes('/usage')) return 'usage';
    if (path.includes('/topup')) return 'topup';
    if (path.includes('/transactions')) return 'transactions';
    return 'usage';
  };

  const getStyles = (key) => {
    const path = location.pathname;
    const styles: any = { color: '#111720' }
    if(path.includes(key)) {
      styles.color = '#007AFF'
    }
    return styles;
  };

  return (
    <div className={styles.usercenter}>
      <aside className={styles.aside}>
        <Menu
          selectedKeys={[getSelectedKey()]}
          mode="inline"
          onClick={({ key }) => handleMenuClick(key)}
          items={[
            {
              key: 'usage',
              icon: <DashboardOutlined style={getStyles('usage')} />,
              label: '用量信息',
            },
            {
              key: 'topup',
              icon: <CreditCardOutlined  style={getStyles('topup')} />,
              label: '充值',
            },
            {
              key: 'transactions',
              icon: <ContainerOutlined style={getStyles('transactions')} />,
              label: '账单',
            },
          ]}
        />
      </aside>
      <main className={styles.main}>
        <Outlet />
      </main>
    </div>
  );
};