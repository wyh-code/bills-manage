import { useState } from 'react';
import { Button, Table, Tag, message, Spin } from 'antd';
import { CheckCircleOutlined, SyncOutlined, CloseCircleOutlined } from '@ant-design/icons';
import Empty from '@/component/Empty';
import { useFileProgress } from '@/hooks/useFileProgress';
import { billApi } from '@/api/bill';
import styles from './index.module.less';

interface BillsProps {
  workspaceId: string;
  uploadResult: any;
  file: any;
  handleReset: any;
}

export default ({ workspaceId, uploadResult, file, handleReset }: BillsProps) => {
  const [spinning, setSpinning] = useState(false);
  const data = uploadResult?.data || {};

  // 使用轮询Hook
  const [store, initStore] = useFileProgress({
    workspaceId,
    fileId: data.file_id,
    onCompleted: (bills) => {
      console.log('处理完成，账单数量:', bills.length);
    },
    onFailed: () => {
      console.error('处理失败');
    },
    pollingInterval: 2000,
  });
  const { status, bills, billsCount, isProcessing } = store as any;

  const columns = [
    {
      title: '卡号',
      dataIndex: 'card_last4',
      width: '10%',
      render: (text: string) => text ? text : '-',
    },
    {
      title: '交易日',
      dataIndex: 'trade_date',
      width: '15%',
    },
    {
      title: '人民币金额',
      dataIndex: 'amount_cny',
      width: '12%',
      render: (text: number) => text ? `¥${text.toFixed(2)}` : '-',
    },
    {
      title: '交易地金额',
      dataIndex: 'amount_foreign',
      width: '13%',
      render: (text: string, record: any) =>
        text ? `${text} ${record.currency || ''}` : '-',
    },
  ];

  // 渲染状态标签
  const renderStatusTag = () => {
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

  const submitBills = async () => {
    try {
      setSpinning(true)
      const res = await billApi.batchConfirm({ 
        workspace_id: workspaceId, file_id: data.file_id, bill_ids: bills?.map(bill => bill.id)
      });
     
      console.log('res: ', res)
      message.success('账单状态更新状态成功');
      handleReset();
      initStore()
    } catch (err: any) {
      message.error(err.message || '批量更新状态失败');
    } finally {
      setSpinning(false)
    }
  }
  return (
    <div className={styles.dataView}>
      <Spin spinning={spinning} />
      <div className={styles.title}>
        <div>解析结果</div>
        {bills.length ? (
          <Button 
            type="primary" 
            disabled={!workspaceId || !data.file_id} 
            onClick={submitBills}
          >
            确认解析结果
          </Button>
        ) : null}
      </div>
      <div className={styles.bills}>
        {
          (data.file_id && isProcessing) ? (
            <div className={styles.billStatus}>
              <div className={styles.billTip}>
                <span>文件状态: {renderStatusTag()}</span>
                <span>账单数量: {billsCount}</span>
              </div>

              <div className={styles.billName}>
                当前文件: {file.name}
              </div>

            </div>
          ) : (
            bills.length ? (
              <Table
                style={{ width: "100%" }}
                dataSource={bills}
                columns={columns}
                rowKey="id"
                pagination={{
                  pageSize: 10,
                  showTotal: (total) => `共 ${total} 条`,
                }}
                scroll={{ x: 'max-content' }}
              />
            ) : (
              <Empty
                style={{ margin: '100px 0px' }}
                description={
                  isProcessing
                    ? '正在解析文件，请稍候...'
                    : status === 'failed'
                      ? '文件解析失败'
                      : '暂无数据'
                }
              />
            )
          )
        }
      </div>
    </div>
  );
};