
import { DatePicker, Tag, InputNumber, Input } from 'antd';
import { CheckCircleOutlined, SyncOutlined, CloseCircleOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import TextBallonWithEllipse from "@/component/TextBallonWithEllipse";
import Link from '@/component/Link';
import { formateTime } from '@/utils/utils';
import styles from './index.module.less';

export const inputKey = ['trade_date', 'record_date', 'amount_cny', 'amount_foreign', 'currency', 'description'];

export const checkRequire = (row) => {
  let isRequire = true;
  inputKey.forEach(key => {
    if (row[key] === undefined || row[key] === null) {
      isRequire = false;
      row[`${key}_tip`] = '不能为空'
    }

    if (['trade_date', 'record_date'].includes(key) && row[key]) {
      row[key] = formateTime(row[key])
    }
  })
  return isRequire
}

export const getColumns = ({ onEdit, onChangeStatus, onRemove }) => {

  const renderCell = (value) => {
    return value || value === 0 ? value : '--';
  }

  const renderInputNumber = (key, value, row) => {
    return (
      <div className={styles.cellContainer}>
        <InputNumber min={0.01} value={value} onChange={(value) => onEdit(key, value, row)} />
        {row[`${key}_tip`] ? <div className={styles.cellTip}>{row[`${key}_tip`]}</div> : null}
      </div>
    )
  }
  const renderInput = (key, value, row) => {
    return (
      <div className={styles.cellContainer}>
        <Input value={value} onChange={(value) => onEdit(key, value.target.value, row)} />
        {row[`${key}_tip`] ? <div className={styles.cellTip}>{row[`${key}_tip`]}</div> : null}
      </div>
    )
  }
  const renderDatePicker = (key, value, row) => {
    return (
      <div className={styles.cellContainer}>
        <DatePicker value={value} onChange={(value) => onEdit(key, value ?? undefined, row)} />
        {row[`${key}_tip`] ? <div className={styles.cellTip}>{row[`${key}_tip`]}</div> : null}
      </div>
    )
  }

  const columns = [
    {
      title: '卡号',
      dataIndex: 'card_last4',
      width: 100,
      render: (text: string, row, index) => row.isEdit ?
        renderInput('card_last4', text, row) :
        renderCell(text),
    },
    {
      title: '交易日',
      dataIndex: 'trade_date',
      width: 115,
      render: (text: string, row, index) => row.isEdit ?
        renderDatePicker('trade_date', text && dayjs(text), row) :
        renderCell(text),
    },
    {
      title: '记账日',
      dataIndex: 'record_date',
      width: 115,
      render: (text: string, row, index) => row.isEdit ?
        renderDatePicker('record_date', text && dayjs(text), row) :
        renderCell(text),
    },
    {
      title: '人民币金额',
      dataIndex: 'amount_cny',
      width: 105,
      render: (text: number, row) => row.isEdit ?
        renderInputNumber('amount_cny', text, row) :
        renderCell(text && `¥${text.toFixed(2)}`),
    },
    {
      title: '交易地金额',
      dataIndex: 'amount_foreign',
      width: 120,
      render: (text: string, row: any) => row.isEdit ?
        renderInputNumber('amount_foreign', text, row) :
        renderCell(text && `${text} ${row.currency || ''}`)
    },
    {
      title: '币种',
      dataIndex: 'currency',
      width: 100,
      render: (text: string, row: any) => row.isEdit ?
        renderInput('currency', text, row) :
        renderCell(text),
    },
    {
      title: '描述',
      dataIndex: 'description',
      width: 100,
      render: (text: string, row) => row.isEdit ?
        renderInput('description', text, row) :
        <TextBallonWithEllipse text={text} line={1} />
    },
    {
      title: '操作',
      dataIndex: 'handler',
      width: 100,
      render: (_, row, index) => (
        <div>
          {
            row.isEdit ?
              <Link onClick={() => onChangeStatus(row)}>保存</Link> :
              <Link onClick={() => onChangeStatus(row)}>编辑</Link>
          }
          <Link style={{ marginLeft: 10 }} onClick={() => onRemove(index)}>删除</Link>
        </div>
      )
    },
  ];

  return columns
}

// 渲染状态标签
export const renderStatusTag = (status, isProcessing) => {
  if (status === 'processing' || isProcessing) {
    return (
      <Tag icon={<SyncOutlined spin />} color="processing">
        解析中
      </Tag>
    );
  }
  if (status === 'completed') {
    return (
      <Tag icon={<CheckCircleOutlined />} color="success">
        已完成
      </Tag>
    );
  }
  if (status === 'failed') {
    return (
      <Tag icon={<CloseCircleOutlined />} color="error">
        解析失败
      </Tag>
    );
  }
  return null;
};

