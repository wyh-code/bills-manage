import { useState } from 'react';
import { message } from 'antd';
import styles from './index.module.less';
import shared from '@/assets/share.svg';
import disabledShare from '@/assets/disabled-share.svg';

export default ({ disabled, className }: any) => {
  const [text, setText] = useState('');
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      message.success('复制成功');
    } catch {
      message.error('复制失败');
    }
  };

  return (
    <div className={`${styles.shared} ${className}`}>
      {
        disabled ? (
          <img className="disabled" src={disabledShare} />
        ) : (
          <img className="active" src={shared} />
        )
      }
      <span>分享</span>
    </div>
  );
};