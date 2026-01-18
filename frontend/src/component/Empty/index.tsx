import icon from '@/assets/404.svg';
import styles from './index.module.less';

interface EmptyIProps {
  iconSize: number, 
  fontSize: number, 
  line: boolean, 
  style: any, 
  description: string, 
  className: string,
}

export default ({ iconSize, fontSize, line, style, description, className }: any) => {

  return (
    <div className={`${styles.empty} ${line ? styles.line : ''} ${className} `} style={style}>
      <img className={styles.icon} src={icon} style={{ width: iconSize, height: iconSize }} />
      <div className={styles.tip} style={{ fontSize }}>{description || '暂无数据'}</div>
    </div>
  )
}
