import { Button } from 'antd';
import dayjs from 'dayjs';
import { FileRecord } from '@/api/upload';
import TextBallonWithEllipse from '@/component/TextBallonWithEllipse';
import Link from '@/component/Link';

const formatAmount = (amounts: Record<string, number>) => {
  return Object.entries(amounts || {})
    .map(([currency, amount]) => `${currency} ${amount.toFixed(2)}`)
    .join(', ');
};

export const getColumns = ({ showBillsModal, onPreview }) => {

  const columns = [
    {
      title: '账务空间',
      dataIndex: ['workspace', 'name'],
      key: 'workspace',
      width: 120,
      ellipsis: true,
    },
    {
      title: '文件名',
      dataIndex: 'file_name',
      key: 'file_name',
      width: 200,
      ellipsis: true,
      render: value => <TextBallonWithEllipse text={value} line={1} />
    },
    {
      title: '上传人',
      dataIndex: ['uploader', 'nickname'],
      key: 'uploader',
      width: 100,
      render: (text: string) => text || '--',
    },
    {
      title: '上传时间',
      dataIndex: 'upload_time',
      key: 'upload_time',
      width: 140,
      render: (text: string) => text ? (
        <span style={{ whiteSpace: 'nowrap' }}>
          {dayjs(text).format('YYYY-MM-DD HH:mm:ss')}
        </span>
      ) : '--',
    },
    {
      title: '账单条数',
      dataIndex: 'bills_count',
      key: 'bills_count',
      width: 100,
      render: (count: number, record: FileRecord) => (
        <Button type="link" onClick={() => showBillsModal(record.bills)}>
          {count}
        </Button>
      ),
    },
    {
      title: '账单总金额',
      dataIndex: 'total_amount',
      key: 'total_amount',
      width: 100,
      render: (amounts: Record<string, number>) => formatAmount(amounts),
    },
    {
      title: '操作',
      dataIndex: 'handler',
      key: 'handler',
      width: 100,
      render: (_, row) => (
        <>
          <Link onClick={() => onPreview(row)}>查看</Link>
        </>
      ),
    },
  ];

  return columns;
}


export const getBillsColumns = () => {

  const billColumns = [
    { title: '发卡行', dataIndex: 'bank', key: 'bank', width: 100 },
    { title: '卡号', dataIndex: 'card_last4', key: 'card_last4', width: 80 },
    { title: '交易日', dataIndex: 'trade_date', key: 'trade_date', width: 120 },
    {
      title: '金额',
      key: 'amount',
      width: 120,
      render: (_: any, record: any) => {
        if (record.amount_cny) {
          return `¥${record.amount_cny}`;
        } else if (record.amount_foreign && record.currency) {
          return `${record.currency} ${record.amount_foreign}`;
        }
        return '--';
      },
    },
    { title: '描述', dataIndex: 'description', key: 'description', ellipsis: true },
  ];

  return billColumns
}