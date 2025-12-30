import { Button } from 'antd';
import Link from '@/component/Link';
import styles from './index.module.less';
import notfound from '@/assets/404.svg';

export default () => {
  return (
    <div className={styles.notfound}>
      <div className={styles.content}>
        <img src={notfound} />
        <div className={styles.contentText}>
          <h4 className={styles.title}>访问的页面不存在</h4>
          <div className={styles.tip} >
            您要找的页面没有找到，请返回<Link to="/">首页</Link>继续浏览
          </div>
        </div>
      </div>
    </div>
  )
}
