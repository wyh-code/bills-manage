import { useNavigate } from 'react-router-dom';
import styles from './index.module.less'

export default ({ children, style, to, type, onClick }: any) => {
  const navigate = useNavigate();

  const clickFunc = (...args) => {
    if(to) {
      navigate(to)
    }
    if(onClick) {
      onClick(...args)
    }
  }

  return (
    <span className={`${styles.link} ${styles[type]}`} style={style} onClick={clickFunc}>
      {children}
    </span>
  )
}