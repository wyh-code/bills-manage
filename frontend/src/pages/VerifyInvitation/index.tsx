import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Input, Button, message } from 'antd';
import { invitationApi } from '@/api/invitation';
import authService from '@/auth/authService';
import styles from './index.module.less';

export default function VerifyInvitation() {
  const navigate = useNavigate();
  const [token, setToken] = useState('');
  const [loading, setLoading] = useState(false);

  const onSubmit = async () => {
    try {
      setLoading(true);
      const result = await invitationApi.join(token);
      message.success(result.message || '验证成功');
      authService.setUser(result.user)
      // 跳转到工作台
      navigate('/dashboard', { replace: true });

    } catch (error: any) {
      message.error(error.message || '邀请码无效');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.verifyInvitation}>
      <div className={styles.container}>
        <Input onChange={(e) => setToken(e.target.value)} placeholder="请输入邀请码以激活账号" disabled={loading} />
        <Button onClick={onSubmit} type="primary" loading={loading}>
          激活
        </Button>
      </div>
    </div>
  );
}