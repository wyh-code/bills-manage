import { useEffect, useState } from 'react';
import { Table, Button, Modal, message, InputNumber } from 'antd';
import Empty from '@/component/Empty';
import { useFileProgress } from '@/hooks/useFileProgress';
import { getColumns, renderStatusTag, inputKey, checkRequire } from './utils';
import ConfirmButton from './ConfirmButton';
import styles from './index.module.less';

interface BillsProps {
  workspaceId: string;
  uploadResult: any;
  file: any;
  handleReset: any;
  setDisabledUpload: any;
}

export default ({ workspaceId, uploadResult, file, handleReset, setDisabledUpload }: BillsProps) => {
  const [selectedRows, setSelectedRows] = useState([]);
  const [datasource, setDatasource] = useState([]);
  const [exchangeRate, setExchangeRate] = useState(7.1);
  const data = uploadResult?.data || {};

  // 使用轮询Hook
  const [{ status, bills, billsCount, isProcessing }] = useFileProgress({
    workspaceId,
    fileId: data.file_id,
    onCompleted: (bills) => {
      console.log('处理完成，账单数量:', bills.length);
      setDisabledUpload(false)
    },
    onFailed: () => {
      message.error('处理失败');
      setDisabledUpload(false)
    },
  });

  const onRowSelectChange = (_, selectedRows, { type }) => {
    if (selectedRows.length && type === 'all') {
      selectedRows = [...bills];
    }
    setSelectedRows(selectedRows);
  }

  const onEdit = (key, value, row) => {
    row[key] = value;
    if (value !== undefined) {
      row[`${key}_tip`] = '';
    }
    if (key === 'currency' && row[key]) {
      row[key] = row[key].toUpperCase()
    }
    console.log(key, row.currency.toLowerCase() === 'usd', row.currency.toLowerCase())
    if (key === 'amount_foreign' && row.currency.toLowerCase() === 'usd') {
      row.amount_cny = Number((value * exchangeRate).toFixed(2))
    }
    row.status = 'modified'
    setDatasource([...datasource])
  }

  const onRemove = (index) => {
    Modal.confirm({
      title: '确定删除该账单？',
      onOk: () => {
        const [row]: any = datasource.splice(index, 1);
        const newSelectedRows = selectedRows.filter(it => {
          return it.id !== row.id
        });
        setSelectedRows(newSelectedRows)
        setDatasource([...datasource])
      }
    })
  }

  const onComplete = (index) => {
    const target = datasource[index];
    const isUsd = target.currency.toLowerCase() === 'usd';
    if (!isUsd) message.error('请先参考账单，将币种修改为USD（美元）')
    if (target.amount_foreign && target.currency.toLowerCase() === 'usd') {
      target.amount_cny = Number((target.amount_foreign * exchangeRate).toFixed(2))
    }
    setDatasource([...datasource])
  }

  const onChangeStatus = (row) => {
    // 必填项校验
    let isRequire = true;
    if (row.isEdit) {
      isRequire = checkRequire(row);
    }
    row.isEdit = !isRequire || !row.isEdit;
    setDatasource([...datasource])
  }

  const addBills = () => {
    const temp = { ...datasource[0], id: +new Date, type: 'add', status: 'modified' };
    Object.keys(temp).forEach(key => {
      if (inputKey.includes(key)) {
        temp[key] = undefined
      }
    })

    datasource.push(temp);
    setDatasource([...datasource])
  }

  const handleResetHandler = () => {
    setDatasource([]);
    handleReset();
  }

  const columns = getColumns({ onEdit, onRemove, onComplete, onChangeStatus });

  useEffect(() => {
    if (bills) {
      setDatasource([...bills])
    }
  }, [bills])

  useEffect(() => {
    if (data.file_id) {
      setDisabledUpload(true)
    }
  }, [data.file_id])

  return (
    <div className={styles.dataView}>
      <div className={styles.title}>
        <div className={styles.name}>
          解析结果
        </div>
        <div className={styles.action}>
          {
            !workspaceId || !data.file_id || isProcessing ? null : (
              <>
                <span className={styles.actionTip}>币种为USD时，修改交易地金额将自动根据汇率补全人民币金额</span>
                <div className={styles.exchangeRate}>
                  <span>美元汇率：</span>
                  <InputNumber
                    value={exchangeRate}
                    onChange={(value) => setExchangeRate(value)}
                  />
                </div>
                <Button type="primary" onClick={addBills} style={{ marginRight: 10 }} >
                  添加账单
                </Button>
              </>
            )
          }
          <ConfirmButton
            handleReset={handleResetHandler}
            workspaceId={workspaceId}
            file_id={data.file_id}
            selectedRows={selectedRows}
            bills={bills}
          />
        </div>
      </div>
      <div className={styles.bills}>
        {
          (data.file_id && isProcessing) ? (
            <div className={styles.billStatus}>
              <div className={styles.billTip}>
                <span>文件状态: {renderStatusTag(status, isProcessing)}</span>
                <span>账单数量: {billsCount}</span>
              </div>

              <div className={styles.billName}>
                当前文件: {file.name}
              </div>
            </div>
          ) : (
            bills.length ? (
              <Table
                rowKey="id"
                dataSource={datasource}
                columns={columns}
                scroll={{ x: 'max-content', y: 480 }}
                rowSelection={{
                  fixed: true,
                  selectedRowKeys: selectedRows.map(item => item.id),
                  onChange: onRowSelectChange
                }}
                pagination={{
                  pageSize: 999,
                  showTotal: (total) => `共 ${total} 条`,
                }}
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