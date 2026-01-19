import { useEffect, useState } from 'react';
import { Drawer, Table, Spin, message, Modal } from 'antd';
import { RightOutlined } from '@ant-design/icons';
import { fileApi, FileRecord } from '@/api/upload';
import FilePreview from '@/component/FilePreview';
import { getColumns, getBillsColumns } from './getCloumns';
import styles from './index.module.less';

export default function FileRecords() {
  const [open, setOpen] = useState(false);
  const [visible, setVisible] = useState(false);
  const [loading, setLoading] = useState(false);
  const [currentRow, setCurrentRow] = useState({});
  const [records, setRecords] = useState<FileRecord[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [billsModalVisible, setBillsModalVisible] = useState(false);
  const [selectedBills, setSelectedBills] = useState<any[]>([]);

  useEffect(() => {
    if (open) {
      fetchFileRecords({ page: 1, page_size: 10 });
    }
  }, [open]);

  const fetchFileRecords = async (searchParams) => {
    try {
      setLoading(true);
      const data = await fileApi.getRecords(searchParams);
      setRecords(data.data);
      setTotal(data.total);
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

  const onPreview = (row) => {
    console.log('row: ', row)
    setCurrentRow(row);
    setVisible(true);
  }

  const columns = getColumns({ showBillsModal, onPreview })
  const billColumns = getBillsColumns();
 

  const onRecordsChange = (page: number) => {
    fetchFileRecords({ page, page_size: 10 });
  }

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
              pageSize: 10,
              total,
              onChange: onRecordsChange,
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