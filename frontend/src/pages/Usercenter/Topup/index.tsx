
import { useState } from 'react';
import { Button } from 'antd';
import { CheckCircleFilled } from '@ant-design/icons';
import alipay from '@/assets/alipay.svg'
import styles from './index.module.less';

export default () => {
  const [current, setCurrent] = useState(10)

  const amounts = [10, 20, 50, 100, 300, 500] 

  return (
    <div className={styles.topup}>
      <div className={styles.pageName}>充值</div>
      <div className={styles.amount}>
        <div className={styles.label}>支付金额</div>
        <div className={styles.value}>
          {
            amounts.map(item => (
              <div 
                className={`${styles.item} ${current === item && styles.active}`}
                onClick={() => setCurrent(item)}
              >
                {item}
              </div>
            ))
          }
        </div>
        <div className={styles.payLabel}>支付方式</div>
        <div className={styles.pay}>
          <div className={styles.item}>
            <img className={styles.alipay} src={alipay} alt="" />
            <CheckCircleFilled />
          </div>
        </div>
        <Button 
          type="primary" 
          className={styles.submit}
        >
          去支付
        </Button>
        <div className={styles.tip}>
          <div className={styles.label}>提示</div>
          <div>
            <div className={styles.value}>1. 充值金额仅用于调用 API 服务。</div>
            <div className={styles.value}>2. 手动录入账单不需要充值。</div>
          </div>
        </div>
      </div>
    </div>
  )
}
