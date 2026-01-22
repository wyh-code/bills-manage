import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button, DatePicker } from 'antd'
import dayjs from 'dayjs';
import { Column, Line } from '@ant-design/plots';
import { accountApi } from '@/api/account';
import { getMonthDaysArray } from '@/utils/utils'
import { getLineConfig, getUsed } from './getConfig';
import styles from './index.module.less'

export default () => {
  const [accountBalance, setAccountBalance] = useState<any>({});
  const [usageMonthly, setUsageMonthly] = useState<any>({});
  const [month, setMonth] = useState(dayjs((new Date()).toLocaleString()).format('YYYY-MM'))
  const navigate = useNavigate();

  const fetAccountBalance = async () => {
    try {
      const accountBalance = await accountApi.balance();
      setAccountBalance(accountBalance)
    } catch (error) {
      console.error('账户余额获取失败:', error);
    }
  }
  const fetUsageMonthly = async () => {
    try {
      const usageMonthly = await accountApi.usageMonthly(month);
      setUsageMonthly(usageMonthly)
    } catch (error) {
      console.error('账户统计获取失败:', error);
    }
  }

  const getMonthly = (daily_stats = []) => {
    const days = getMonthDaysArray(month);
    const usedList = [];
    const apiList = [];
    const tokenList = [];

    const stats = daily_stats.reduce((obj, item) => {
      obj[item.date] = item
      return obj;
    }, {})

    days.forEach(day => {
      if (stats[day]) {
        usedList.push({ day, value: stats[day].amount })
        apiList.push({ day, value: stats[day].api_calls })
        tokenList.push({ day, value: stats[day].tokens })
      } else {
        usedList.push({ day, value: 0 })
        apiList.push({ day, value: 0 })
        tokenList.push({ day, value: 0 })
      }
    })

    return { usedList, apiList, tokenList }
  }

  const onExport = async () => {
    try {
      await accountApi.export(month);
    } catch (error) {
      console.error('账户统计获取失败:', error);
    }
  }

  useEffect(() => {
    fetAccountBalance();
  }, []);

  useEffect(() => {
    fetUsageMonthly()
  }, [month])

  const { usedList, apiList, tokenList } = getMonthly(usageMonthly.daily_stats)

  return (
    <div className={styles.usage}>
      <div className={styles.pageName}>用量信息</div>
      <div className={styles.amount}>
        <div className={styles.amountTotal}>
          <div className={styles.label}>充值余额</div>
          <div className={styles.value}>
            ¥{accountBalance.balance || 0.00}
            <span className={styles.unit}>CNY</span>
          </div>
        </div>
        <div className={styles.amountTotal}>
          <div className={styles.label}>历史消耗</div>
          <div className={styles.value}>
            ¥{accountBalance.total_consumed || 0.00}
            <span className={styles.unit}>CNY</span>
          </div>
        </div>
      </div>
      <Button
        type="primary"
        style={{ background: '#000' }}
        onClick={() => navigate('/usercenter/topup')}
      >
        去充值
      </Button>
      <div className={styles.used}>
        <div className={styles.name}>每月用量</div>
        <div>
          <DatePicker.MonthPicker onChange={v => setMonth(dayjs(v).format('YYYY-MM'))} />
          <Button
            type="primary"
            style={{ background: '#000', marginLeft: 20 }}
            onClick={onExport}
          >
            导出
          </Button>
        </div>
      </div>

      <div className={styles.chart}>
        <Column {...getUsed(usedList)} />
      </div>
      <div className={styles.lineChart}>
        <div className={styles.title}>deepseek-chat</div>
        <div className={styles.lines}>
          <div className={styles.item}>
            <div className={styles.name}>
              API 请求次数
              <span>12</span>
            </div>
            <Line {...getLineConfig(apiList)} />
          </div>
          <div className={styles.item}>
            <div className={styles.name}>
              Tokens
              <span>12</span>
            </div>
            <Line {...getLineConfig(tokenList)} />
          </div>
        </div>
      </div>
    </div>
  )
}
