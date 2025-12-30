import { Popover } from 'antd';
import styles from './index.module.less';

function TextBallonWithEllipse(props: any) {
  const { text, className } = props;

  return (
    <Popover placement="top" content={text}>
      <div className={`${styles.ellipsis2} ${className}`}>{text}</div>
    </Popover>
  );
}

export default TextBallonWithEllipse;
