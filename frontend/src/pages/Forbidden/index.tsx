import Link from '@/component/Link';
import styles from './index.module.less';  // 确保这样导入
import forbidden from '@/assets/403.svg';

function Forbidden() {
  const queryString = window.location.search;
  const params: any = new URLSearchParams(queryString);
  const pathname = params.get('pathname');

  const onApply = () => {
    console.log('onApply');
  };

  return (
    <div className={styles.forbidden}>
      <div className={styles.content}>
        <img src={forbidden} alt="403" />
        <div className={styles.contentText}>
          <h4>暂无访问权限</h4>
          <div className={styles.tip}>
            <p>请先申请访问权限：<Link><span onClick={onApply}>去申请</span></Link></p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Forbidden;
