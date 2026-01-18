import { message, Modal, Input } from "antd";
import Link from "@/component/Link";
import TextBallonWithEllipse from "@/component/TextBallonWithEllipse";
import { billApi } from '@/api/bill';
import Status from "@/component/Status";
import styles from './index.module.less'

export const getColumns = ({ setUpdate }) => {

  const onConfirm = (row) => {
    row.status = 'active';
    billApi.update(row).then(res => {
      setUpdate(+new Date);
      message.success('账单状态已更新')
    })
  }

  const onPay = (row) => {
    Modal.confirm({
      title: '确认支付账单',
      content: (
        <>
          <div className={styles.confirm}>
            <p key={row.id}>
              <span>{row.bank}</span> -
              <span>{row.card_last4}</span> -
              <span>{row.trade_date}</span> -
              <span>{`¥ ${row.amount_cny}` || `${row.currency} ${row.amount_foreign}`}</span>
            </p>
          </div>
          <div>
            <div style={{ margin: '10px 0px 4px', color: '#3e495c', fontSize: 12, fontWeight: 500 }}>备注：</div>
            <Input.TextArea
              placeholder="请输入备注"
              onChange={(e) => row.remark = e.target.value}
            />
          </div>
        </>
      ),
      onOk: () => {
        row.status = 'payed';
        billApi.update(row).then(res => {
          setUpdate(+new Date);
          message.success('账单状态已更新')
        })
      }
    })
  }

  const columns = [
    {
      title: '发卡行',
      width: 100,
      dataIndex: 'bank',
      key: 'back',
    },
    {
      title: '卡号',
      width: 100,
      dataIndex: 'card_last4',
      key: 'card_last4',
    },
    {
      title: '账务空间',
      width: 100,
      dataIndex: 'workspace_id',
      key: 'workspace_id',
    },
    {
      title: '交易日期',
      width: 100,
      dataIndex: 'trade_date',
      key: 'trade_date',
    },
    {
      title: '记账金额',
      width: 100,
      dataIndex: 'amount_foreign',
      key: 'amount_foreign',
    },
    {
      title: '人民币金额',
      width: 100,
      dataIndex: 'amount_cny',
      key: 'amount_cny',
    },
    {
      title: '描述',
      dataIndex: 'description',
      width: 200,
      render: description => <TextBallonWithEllipse line={1} text={description} />
    },
    {
      title: '状态',
      width: 100,
      dataIndex: 'status',
      key: 'status',
      render: (value) => <Status type={value} />
    },
    {
      title: '结算备注',
      dataIndex: 'remark',
      width: 200,
      render: remark => <TextBallonWithEllipse line={1} text={remark} />
    },
    {
      title: '操作',
      width: 100,
      dataIndex: 'handler',
      key: 'handler',
      render: (value, row) => {
        console.log(row.status !== 'pending', row.status)
        return (
          <div className={styles.handler}>
            <Link
              onClick={() => onPay(row)}
              disabled={row.status === 'payed'}
            >
              结算
            </Link>
            <Link
              style={{ marginLeft: 12 }}
              onClick={() => onConfirm(row)}
              disabled={row.status !== 'pending'}
            >
              确认
            </Link>
          </div>
        )
      }
    },
  ];

  return columns
}
