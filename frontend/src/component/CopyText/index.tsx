import { CSSProperties } from 'react';
import { message } from 'antd';
import { CopyOutlined } from '@ant-design/icons';
import styles from './index.module.less';


interface CopyTextProps {
  text: string;
  textStyle?: CSSProperties;
  iconStyle?: CSSProperties;
}

export default ({ text, iconStyle, textStyle }: CopyTextProps) => {
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      message.success('复制成功');
    } catch {
      message.error('复制失败');
    }
  };

  return (
    <div className={styles.copyText}>
      <span style={{ ...textStyle }}>{text}</span>
      <CopyOutlined
        onClick={handleCopy}
        style={{ cursor: 'pointer', ...iconStyle }}
      />
    </div>
  );
};