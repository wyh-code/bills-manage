import { Popover } from 'antd';
import styles from './index.module.less';

function TextBallonWithEllipse(props: any) {
  const { text, className, line } = props;

  return (
    text ? (
      <Popover placement="top" content={text}>
        <div className={`${styles.ellipsis} ${styles[`ellipsis${line || 2}`]} ${className}`}>{text}</div>
      </Popover>
    ) : '--'
  );
}

export default TextBallonWithEllipse;
