import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { message, Drawer, Table } from 'antd';
import dayjs from "dayjs";
import { CopyOutlined, ReloadOutlined, RightOutlined } from '@ant-design/icons';
import { invitationApi, InvitationUseRecord } from '@/api/invitation';
import { accountApi } from '@/api/account';
import authService from '@/auth/authService';
import Link from '@/component/Link';
import Empty from '@/component/Empty';
import TextBallonWithEllipse from '@/component/TextBallonWithEllipse';
import { ROLE_TYPE, INVITATION_TYPE } from '@/utils/const';
import styles from './index.module.less';

export default function InvitationPanel() {
  const [accountAmount, setAccountAmount] = useState(0);
  const [invitationToken, setInvitationToken] = useState('');
  const [drawerVisible, setDrawerVisible] = useState(false);
  const [allUsed, setAllUsed] = useState<InvitationUseRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const user = authService.getUser();
  const navigate = useNavigate();

  useEffect(() => {
    fetchInvitation();
    fetchAllUses();
    fetAccountAmount();
  }, []);

  const fetAccountAmount = async () => {
    try {
      const accountBalance = await accountApi.balance();
      setAccountAmount(accountBalance.balance)
    } catch (error) {
      console.error('账户余额获取失败:', error);
    }
  }

  const fetchInvitation = async () => {
    try {
      const invitations = await invitationApi.list({ type: 'platform' });
      const activeInvitation = invitations.find(inv =>
        inv.status === 'active' && new Date(inv.expires_at) > new Date()
      );
      if (activeInvitation) {
        setInvitationToken(activeInvitation.token);
      }
    } catch (error) {
      console.error('获取邀请码失败:', error);
    }
  };

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(invitationToken);
      message.success('复制成功');
    } catch {
      message.error('复制失败');
    }
  };

  const handleRefresh = async () => {
    try {
      setLoading(true);
      const result = await invitationApi.create({ type: 'platform' });
      setInvitationToken(result.token);
      message.success('刷新成功');
      fetchAllUses();
    } catch (error: any) {
      message.error(error.message || '刷新失败');
    } finally {
      setLoading(false);
    }
  };

  const fetchAllUses = async () => {
    try {
      const uses = await invitationApi.getUses();
      setAllUsed(uses);
    } catch (error: any) {
      message.error(error.message || '获取历史记录失败');
    }
  };

  const columns = [
    {
      title: '邀请时间',
      dataIndex: 'invitation_created_at',
      key: 'invitation_created_at',
      width: 180,
      render: (text: string) => text ? new Date(text).toLocaleString() : '--',
    },
    {
      title: '使用人',
      dataIndex: 'user',
      key: 'user',
      width: 120,
      render: (user) => (
        <div className={styles.cellItem}>
          <img src={user.headimgurl} alt="" />
          <span>{user.nickname}</span>
        </div>
      )
    },
    {
      title: '同意时间',
      dataIndex: 'used_at',
      key: 'used_at',
      width: 180,
      render: (text: string) => text ? dayjs(text).format('YYYY-MM-DD HH:mm:ss') : '--',
    },
    {
      title: '邀请类型',
      dataIndex: 'invitation_type',
      key: 'invitation_type',
      width: 100,
      render: (type: string) => INVITATION_TYPE[type],
    },
    {
      title: '用户角色',
      dataIndex: 'role',
      key: 'role',
      width: 100,
      render: (type: string) => ROLE_TYPE[type],
    },
    {
      title: '操作',
      dataIndex: 'handler',
      key: 'handler',
      width: 100,
      render: (_, row) => (
        <>
          <Link>删除</Link>
        </>
      ),
    },
  ];

  return (
    <div className={styles.invitationPanel}>
      <div className={styles.userInfo}>
        <img src={user?.headimgurl} alt="avatar" className={styles.avatar} />
        <div className={styles.userRow}>
          <TextBallonWithEllipse className={styles.username} line={1} text={user?.nickname || '用户'} />
          <div className={styles.username}>
          </div>
          <div className={styles.account}>
            <div className={styles.accountAmount}>
              <div className={styles.label}>余额:</div>
              <div className={styles.amount}>¥{accountAmount.toFixed(2)}</div>
            </div>
            <div className={styles.usercenter} onClick={() => navigate('/usercenter')}>
              <span>个人中心</span>
              <RightOutlined />
            </div>
          </div>
        </div>
      </div>

      <div className={styles.infoItem}>
        <div className={styles.label}>邀请码</div>
        <div className={styles.tokenRow}>
          <div className={styles.token}>{invitationToken || '点击刷新获取邀请码'}</div>
          <CopyOutlined onClick={handleCopy} className={styles.icon} />
          <ReloadOutlined
            onClick={handleRefresh}
            className={styles.icon}
            spin={loading}
          />
        </div>
      </div>

      <div className={styles.records}>
        <div className={styles.recordsHeader}>
          <div className={styles.label}>邀请记录</div>
          <Link onClick={() => setDrawerVisible(true)}>详情</Link>
        </div>
        <div className={styles.recordsList}>
          {allUsed.length > 0 ? (
            allUsed.slice(0, 5).map((item, index) => (
              <div key={index} className={styles.recordItem}>
                <div className={styles.user}>
                  <img src={item.user?.headimgurl} />
                  <TextBallonWithEllipse line={1} text={item.user?.nickname} />
                </div>
                <div className={styles.time}>
                  {dayjs(item.used_at).format('YYYY-MM-DD HH:mm:ss')}
                </div>
              </div>
            ))
          ) : (
            <Empty className={styles.emptyRecords} description="暂无邀请记录" />
          )}
        </div>
      </div>

      <Drawer
        title="邀请历史记录"
        placement="right"
        onClose={() => setDrawerVisible(false)}
        open={drawerVisible}
        size={800}
      >
        <Table
          columns={columns}
          dataSource={allUsed}
          rowKey={(record, index) => `${record.user.openid}-${index}`}
          pagination={{
            pageSize: 20,
            showTotal: (total) => `共 ${total} 条`,
          }}
        />
      </Drawer>
    </div>
  );
}