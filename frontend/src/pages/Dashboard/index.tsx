import { useEffect, useState } from 'react';
import { invitationApi } from '@/api/invitation';
import { getUrlParams } from '@/utils/utils';
import { generateDonutChartSVG } from '@/utils/svg';
import Worksapce from './Worksapce';
import CostView from './CostView';
import styles from './index.module.less';

function Dashboard() {
  const [joined, setJoined] = useState(0);

  const svg = generateDonutChartSVG(
    [{ color: '#FF6619', scale: 90 }, { color: '#007AFF', scale: 60 }],
    [26, 15]
  )

  const jionToken = getUrlParams('join');

  useEffect(() => {
    if (jionToken) {
      invitationApi.join(jionToken).then(res => {
        console.log('res: ', res)
        setJoined(+new Date)
      })
    }
  }, [jionToken])

  return (
    <div className={styles.dashboard}>
      <div className={styles.content}>
        <div className={styles.overview}>
          <div className={styles.title}>
            <div className={styles.name}>数据概览</div>
            <div className={styles.tip}>数据统计截止至：2025/12/30</div>
          </div>
          <div className={styles.item}>
            <div className={styles.title}>
              <div className={styles.name}>费用概览</div>
              <CostView />
            </div>
            <div className={styles.detail}>
              <div className={styles.cost}>
                <div className={styles.count}>
                  <div className={styles.amount}>2345</div>
                  <div className={styles.currency}>CNY</div>
                </div>
                <div className={styles.tip}>账单总额</div>
              </div>
              <div className={styles.info}>
                <div className={styles.infoItem}>
                  <div className={styles.count}>
                    <div className={styles.amount}>2345</div>
                    <div className={styles.currency}>CNY</div>
                  </div>
                  <div className={styles.tip}>已结算金额</div>
                </div>
                <div className={styles.infoItem}>
                  <div className={styles.count}>
                    <div className={styles.amount}>2345</div>
                    <div className={styles.currency}>CNY</div>
                  </div>
                  <div className={styles.tip}>未结算金额</div>
                </div>
                <div className={styles.chartItem}>
                  <div className={styles.chart} dangerouslySetInnerHTML={{ __html: svg }} />
                  <div className={styles.tip}>
                    <div className={styles.payed}>
                      已结算 30%
                    </div>
                    <div className={styles.unpay}>
                      未结算 70%
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <Worksapce joined={joined} />
      </div>
      <div className={styles.side}>
        <div className={styles.message}>
          <div className={styles.title}>
            <div className={styles.name}>通知中心</div>
            <div className={styles.tip}>更多</div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
