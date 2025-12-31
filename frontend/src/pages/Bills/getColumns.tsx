import Link from "@/component/Link";
import styles from './index.module.less'

export const getColumns = () => {
  const columns = [
    {
      title: '发卡行',
      width: 100,
      dataIndex: 'bank',
      key: 'name',
    },
    {
      title: '卡号',
      width: 100,
      dataIndex: 'card',
      key: 'card',
    },
    {
      title: '账务空间',
      width: 100,
      dataIndex: 'card',
      key: 'card',
    },
    {
      title: '交易日期',
      width: 100,
      dataIndex: 'card',
      key: 'card',
    },
    {
      title: '记账金额',
      width: 100,
      dataIndex: 'card',
      key: 'card',
    },
    {
      title: '人民币金额',
      width: 100,
      dataIndex: 'card',
      key: 'card',
    },
    {
      title: '操作',
      width: 100,
      dataIndex: 'handler',
      key: 'handler',
      render: (value, index, row) => {

        return (
          <div className={styles.handler}>
            <Link>结算</Link>
            <div className={styles.reset}>恢复</div>
          </div>
        )
      }
    },
  ];

  return columns
}
