import { useEffect, useState } from 'react';
import { Drawer, Table, Spin, message, Modal, Button } from 'antd';
import { RightOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import { fileApi, FileRecord } from '@/api/upload';
import FilePreview from '@/component/FilePreview';
import TextBallonWithEllipse from '@/component/TextBallonWithEllipse';
import Link from '@/component/Link';
import styles from './index.module.less';

export default function FileRecords() {
  const [open, setOpen] = useState(false);
  const [visible, setVisible] = useState(false);
  const [loading, setLoading] = useState(false);
  const [currentRow, setCurrentRow] = useState({});
  const [records, setRecords] = useState<FileRecord[]>([]);
  const [billsModalVisible, setBillsModalVisible] = useState(false);
  const [selectedBills, setSelectedBills] = useState<any[]>([]);

  useEffect(() => {
    if (open) {
      fetchFileRecords();
    }
  }, [open]);

  const fetchFileRecords = async () => {
    try {
      setLoading(true);
      const data = await fileApi.getRecords();
      setRecords(data);
    } catch (error: any) {
      message.error(error.message || '获取文件记录失败');
    } finally {
      setLoading(false);
    }
  };

  const showBillsModal = (bills: any[]) => {
    setSelectedBills(bills);
    setBillsModalVisible(true);
  };

  const formatAmount = (amounts: Record<string, number>) => {
    return Object.entries(amounts || {})
      .map(([currency, amount]) => `${currency} ${amount.toFixed(2)}`)
      .join(', ');
  };

  const onPreview = (row) => {
    console.log('row: ', row)
    setCurrentRow(row);
    setVisible(true);
  }

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
      width: 120,
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

  const billColumns = [
    { title: '发卡行', dataIndex: 'bank', key: 'bank', width: 100 },
    { title: '卡号', dataIndex: 'card_last4', key: 'card_last4', width: 80 },
    { title: '交易日', dataIndex: 'trade_date', key: 'trade_date', width: 100 },
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

  return (
    <div className={styles.fileRecords}>
      <div className={styles.name} onClick={() => setOpen(true)}>
        <span>详情</span>
        <RightOutlined />
      </div>
      <Drawer
        title="文件上传记录"
        placement="right"
        onClose={() => setOpen(false)}
        open={open}
        size={1000}
      >
        <Spin spinning={loading}>
          <Table
            columns={columns}
            dataSource={records}
            rowKey="file_id"
            pagination={{
              pageSize: 20,
              showTotal: (total) => `共 ${total} 条`,
            }}
          />
        </Spin>
      </Drawer>

      <Drawer
        open={visible}
        title="原始账单"
        onClose={() => setVisible(false)}
        size={1200}
      >
        <FilePreview
          fileId={(currentRow as any)?.file_id}
          workspaceId={(currentRow as any)?.workspace?.id}
        />
      </Drawer>
      <Modal
        title="账单明细"
        open={billsModalVisible}
        onCancel={() => setBillsModalVisible(false)}
        width={800}
        footer={null}
      >
        <Table
          columns={billColumns}
          dataSource={selectedBills}
          rowKey="id"
          pagination={false}
          scroll={{ y: 400 }}
        />
      </Modal>
    </div>
  );
}