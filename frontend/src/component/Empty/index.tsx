import icon from '@/assets/404.svg';
import styles from './index.module.less';

export default ({ iconSize, fontSize, line, style }: any) => {

  return (
    <div className={`${styles.empty} ${line ? styles.line : ''}`} style={style}>
      <img className={styles.icon} src={icon} style={{ width: iconSize, height: iconSize }} />
      <div className={styles.tip} style={{ fontSize }}>暂无数据</div>
    </div>
  )
}
