import { useState } from 'react';
import { Button, message, Modal, Typography } from 'antd';
import { billApi } from '@/api/bill';
import { getTotalCount, checkRequire } from './utils'
import styles from './index.module.less';

const { Text } = Typography;

interface ConfirmButtonProps {
  workspaceId: string;
  file_id: string;
  bills: any;
  handleReset: any;
  selectedRows: any;
}

export default ({ workspaceId, file_id, selectedRows, bills, handleReset }: ConfirmButtonProps) => {
  const [visible, setVisible] = useState(false);
  const [spinning, setSpinning] = useState(false);
  const [failedResultIds, setFailedResultIds] = useState([]);

  const confirmBills = () => {
    const isEdit = selectedRows.some(item => item.isEdit);
    if (isEdit) return message.error('请先保存所有选中项')
    const isRequire = selectedRows.every(row => checkRequire(row));
    if (!isRequire) return message.error('所有选中项内容必须有值')
    setVisible(true)
  }

  const onConfirm = async () => {
    try {
      setSpinning(true)
      const adds = [];
      const updates = [];
      selectedRows.forEach(item => {
        if (item.type === 'add') {
          adds.push(item)
        } else {
          updates.push({ ...item, status: 'active' })
        }
      })
      const promises = [];
      if (adds.length) {
        promises.push(billApi.batchCreate({ workspace_id: adds[0].workspace_id, data: adds }));
      }
      if (updates.length) {
        promises.push(billApi.batchUpdate({ workspace_id: selectedRows[0].workspace_id, data: updates }));
      }
      const [createResult, updataResult] = await Promise.all(promises);

      let failedResultIds = [];
      if (createResult?.failed_count) {
        message.error(`新增账单失败${createResult.failed_count}条`);
        failedResultIds = failedResultIds.concat(createResult.results.filter(item => !item.success))
      }

      if (updataResult?.failed_count) {
        message.error(`账单更新失败${createResult.failed_count}条`);
        failedResultIds = failedResultIds.concat(updataResult.results.filter(item => !item.success))
      }

      if (!updataResult?.failed_count && !createResult?.failed_count) {
        message.success('账单状态更新状态成功');
      }
      setFailedResultIds(failedResultIds.map(it => it.bill_id));
      handleReset();
    } catch (err: any) {
      message.error(err.message || '批量更新状态失败');
    } finally {
      setSpinning(false);
      setVisible(false);
    }
  }

  const totalCount = getTotalCount(selectedRows)

  return (
    bills.length ?
      <>
        <Button
          type="primary"
          disabled={!workspaceId || !file_id || !selectedRows.length}
          onClick={confirmBills}
        >
          确认账单
        </Button>
        <Modal
          loading={spinning}
          open={visible}
          title={(
            <>
              确认账单汇总：
              {
                totalCount.length ? (
                  <div>
                    {totalCount.map(([currency, count]) => (
                      <Text strong key={currency} style={{ marginRight: 10, color: '#FF6619' }}>
                        {currency}: {(count as number).toFixed(2)}
                      </Text>
                    ))}
                  </div>
                ) : null
              }
            </>
          )}
          onCancel={() => setVisible(false)}
          footer={(
            <div>
              <Button onClick={onConfirm} type="primary">确定</Button>
              <Button style={{ marginLeft: 8 }} onClick={() => setVisible(false)}>
                取消
              </Button>
            </div>
          )}
        >
          <div className={styles.confirm}>
            {
              selectedRows.map(item => (
                <p key={item.id} className={`${failedResultIds.includes(item.id) ? styles.failed : ''}`}>
                  <span>{item.bank}</span> -
                  <span>{item.card_last4}</span> -
                  <span>{item.trade_date}</span> -
                  <span>{`¥ ${item.amount_cny}` || `${item.currency} ${item.amount_foreign}`}</span>
                </p>
              ))
            }
          </div>
        </Modal>
      </> : null
  )
}
