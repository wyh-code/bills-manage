import { useEffect, useState } from 'react';
import { Button } from 'antd';
import dayjs from 'dayjs';
import { invitationApi } from '@/api/invitation';
import { billApi } from '@/api/bill';
import { getUrlParams } from '@/utils/utils';
import { generateDonutChartSVG } from '@/utils/svg';
import Worksapce from './Worksapce';
import FileRecords from './FileRecords';
import InvitationPanel from './InvitationPanel';
import styles from './index.module.less';

function Dashboard() {
  const [joined, setJoined] = useState(0);
  const [summary, setSummary] = useState<any>({});

  const settled_percentage = [undefined, null].includes(summary.settled_percentage) ? 100 : summary.settled_percentage;
  const joinToken = getUrlParams('join');

  useEffect(() => {
    if (joinToken) {
      invitationApi.join(joinToken).then(res => {
        setJoined(+new Date);
      });
    }
  }, [joinToken]);

  useEffect(() => {
    fetchSettlementSummary();
  }, []);

  const fetchSettlementSummary = async () => {
    try {
      const data = await billApi.getSettlementSummary();
      setSummary(data);
    } catch (error) {
      console.error('获取结算汇总失败:', error);
    }
  };

  const svg = generateDonutChartSVG(
    [
      { color: '#FF6619', scale: summary.settled_percentage },
      { color: '#007AFF', scale: 100 - settled_percentage }
    ],
    [26, 15]
  );

  const formatAmount = (amounts?: Record<string, number>) => {
    let entries = Object.entries(amounts || {});
    entries = entries.length ? entries : [['CNY', 0]]
    return entries.map(([currency, amount]) => (
      <div key={currency} className={styles.count}>
        <div className={styles.amount}>{(amount || 0).toFixed(2)}</div>
        <div className={styles.currency}>{currency || 'CNY'}</div>
      </div>
    ));
  };

  return (
    <div className={styles.dashboard}>
      <div className={styles.content}>
        <div className={styles.overview}>
          <div className={styles.title}>
            <div className={styles.name}>数据概览</div>
            <div className={styles.tip}>数据统计截止至: {dayjs().format('YYYY-MM-DD')}</div>
          </div>
          <div className={styles.item}>
            <div className={styles.title}>
              <div className={styles.name}>费用概览</div>
              <FileRecords />
            </div>
            <div className={styles.detail}>
              <div className={styles.cost}>
                {summary?.total ? formatAmount(summary?.total) : (
                  <div className={styles.noamount}>暂无数据</div>
                )}

                <div className={styles.tip}>账单总额</div>
              </div>
              <div className={styles.info}>
                <div className={styles.infoItem}>
                  {
                    summary?.settled ? formatAmount(summary?.settled) : (
                      <div className={styles.noamount}>暂无数据</div>
                    )
                  }
                  <div className={styles.tip}>已结算金额</div>
                </div>
                <div className={styles.infoItem}>
                  {
                    summary?.unsettled ? formatAmount(summary?.unsettled) : (
                      <div className={styles.noamount}>暂无数据</div>
                    )
                  }

                  <div className={styles.tip}>未结算金额</div>
                </div>
                <div className={styles.chartItem}>
                  <div className={styles.chart} dangerouslySetInnerHTML={{ __html: svg }} />
                  {
                    summary?.total ? (
                      <div className={`${styles.tip} ${[null, undefined].includes(summary.settled_percentage) && styles.settled}`}>
                        <div className={styles.payed}>
                          已结算 {summary.settled_percentage || 0}%
                        </div>
                        <div className={styles.unpay}>
                          未结算 {100 - settled_percentage}%
                        </div>
                      </div>
                    ) : <div className={styles.tip}>暂无数据</div>
                  }
                </div>
              </div>
            </div>
          </div>
        </div>
        <Worksapce joined={joined} />
      </div>
      <div className={styles.side}>
        <InvitationPanel />
      </div>
    </div>
  );
}

export default Dashboard;