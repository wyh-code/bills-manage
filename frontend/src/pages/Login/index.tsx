import { useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { message } from 'antd';
import { Authmate } from '@ostore/authmate';
import authService from '@/auth/authService';
import { getUrlParams } from '@/utils/utils';
import styles from './index.module.less';

export default () => {
  const navigate = useNavigate();
  const isFetch = useRef(false);
  const authmateRef = useRef<any>(null);

  useEffect(() => {
    // 检查是否已登录
    const token = authService.getToken();
    if (token) {
      navigate('/dashboard', { replace: true });
      return;
    }

    // 初始化微信登录
    if (isFetch.current) return;
    isFetch.current = true;

    const initWechatLogin = async () => {
      try {
        authmateRef.current = Authmate.wechat({
          container: 'login_container',
          fetchBase: 'http://127.0.0.1:7788/api',
          onQrRefresh: () => {
            message.info('二维码已刷新');
          },
          onError: (error) => {
            console.error('登录错误:', error);
            message.error('登录失败，请重试');
          },
        });
        const userInfo = await authmateRef.current.login();
        if (userInfo?.token) {
          // token存储
          authService.wechatLogin(userInfo);
          message.success('登录成功');
          const back_url = getUrlParams('back_url');
          if(back_url) {
            navigate(back_url, { replace: true })
          } else {
            navigate('/dashboard', { replace: true })
          }
        } else {
          message.error('登录失败，未获取到授权码');
        }
      } catch (error) {
        console.error('登录流程错误:', error);
        message.error('登录失败');
      }
    };

    initWechatLogin();

    // 清理
    return () => {
      authmateRef.current?.destroy();
    };
  }, []);

  return (
    <div className={styles.login}>
      <div className={styles.loginContainer}>
        <div id="login_container" />
      </div>
    </div>
  );
}
