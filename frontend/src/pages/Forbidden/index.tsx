import Link from '@/component/Link';
import styles from './index.module.less';  // 确保这样导入
import noRights from '@/assets/403.svg';

function Forbidden() {

  const onApply = () => {
    console.log('onApply');
  };

  return (
    <div className={styles.noRights}>
      <div className={styles.content}>
        <img src={noRights} alt="403" />
        <div className={styles.contentText}>
          <h4>您暂时无权限访问</h4>
          <div className={styles.tip}>
            <p>新用户请先申请访问权限：<Link><span onClick={onApply}>去申请</span></Link></p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Forbidden;
