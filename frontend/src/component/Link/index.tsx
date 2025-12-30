import { useNavigate } from 'react-router-dom';
import styles from './index.module.less'

export default ({ children, style, to }: any) => {
  const navigate = useNavigate();

  return (
    <span className={styles.link} style={style} onClick={() => to && navigate(to)}>
      {children}
    </span>
  )
}