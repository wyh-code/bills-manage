import { useCallback, useEffect, useState } from 'react';
import { Table, Form, Select, Row, Col, DatePicker, Button, message, Spin, Modal, Typography, Input } from 'antd';
import { billApi } from '@/api/bill';
import { workspaceApi } from "@/api/workspace";
import { getTotalCount } from '@/utils/utils';
import { getColumns } from './getColumns'
import styles from './index.module.less';

const { Text } = Typography;

export default () => {
  const [datasource, setDatasource] = useState([]);
  const [total, setTotal] = useState(0);
  const [workspaces, setWorkspaces] = useState([]);
  const [cards, setCards] = useState([]);
  const [selectedRows, setSelectedRows] = useState([]);
  const [spinning, setSpinning] = useState(false);
  const [searchParams, setSearchParams] = useState({ page: 1, page_size: 10 });
  const [update, setUpdate] = useState(0);
  const [visible, setVisible] = useState(false);
  const [remark, setRemark] = useState('');

  const fetchDatasource = useCallback(() => {
    setSpinning(true)
    billApi.list(searchParams).then(res => {
      setDatasource(res.items)
      setTotal(res?.total)
    }).catch(error => {
      message.error(error.message)
    }).finally(() => setSpinning(false))
  }, [searchParams, update])

  const fetchWorkspace = () => {
    workspaceApi.list().then(res => {
      const options = (res || []).map(workspace => ({ label: workspace.name, value: workspace.id }))
      setWorkspaces(options);
    }).catch((error: any) => {
      message.error(error.message)
    })
  }

  const fetchCards = async () => {
    billApi.getCardList().then(res => {
      const options = (res || []).map(card => ({ label: card.card_last4, value: card.card_last4 }))
      setCards(options);
    }).catch(error => {
      message.error(error.message)
    })
  }

  const columns = getColumns({ setUpdate }) as any;

  const onRowSelectChange = (selectedRowKeys, selectedRows, { type }) => {
    if (selectedRows.length && type === 'all') {
      selectedRows = [...datasource];
    }
    setSelectedRows(selectedRows);
  }

  const onConfirm = () => {
    billApi.batchUpdate({
      workspace_id: selectedRows[0].workspace_id,
      data: selectedRows.map(item => ({ ...item, status: 'payed', remark }))
    }).then(res => {
      setVisible(false);
      setSearchParams({ ...searchParams });
      setSelectedRows([]);
    })
  }

  const onFinish = (values) => {
    if (values.date) {
      values.start_date = values.date[0].format('YYYY-MM-DD');
      values.end_date = values.date[1].format('YYYY-MM-DD');
    }
    setSearchParams({ ...searchParams, ...values });
    setSelectedRows([]);
  }

  const onReset = () => {
    setSearchParams({ page: 1, page_size: 10 });
    setSelectedRows([]);
  }

  const onPaginationChange = (page: number) => {
    setSearchParams({ ...searchParams, page });
    setSelectedRows([]);
  }

  useEffect(() => {
    fetchWorkspace();
    fetchCards()
  }, [])

  useEffect(() => {
    fetchDatasource();
  }, [fetchDatasource])

  const totalCount = getTotalCount(selectedRows)

  return (
    <div className={styles.bills}>
      <Spin spinning={spinning}>
        <Form
          onFinish={onFinish}
          onReset={onReset}
          className={styles.form}
        >
          <Row gutter={30}>
            <Col span={5}>
              <Form.Item label="账务空间" name="workspace_ids" style={{ marginBottom: 0 }}>
                <Select placeholder="请选择账务空间" mode="multiple" options={workspaces} />
              </Form.Item>
            </Col>
            <Col span={5}>
              <Form.Item label="卡号" name="card_last4_list" style={{ marginBottom: 0 }}>
                <Select placeholder="请选择卡号" mode="multiple" options={cards} />
              </Form.Item>
            </Col>
            <Col span={5}>
              <Form.Item label="日期" name="date" style={{ marginBottom: 0 }}>
                <DatePicker.RangePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={5}>
              <Form.Item label="状态" name="status_list" style={{ marginBottom: 0 }}>
                <Select
                  mode="multiple"
                  placeholder="请选择状态"
                  options={[
                    { label: '待确定', value: 'pending' },
                    { label: '已确定', value: 'active' },
                    { label: '已修改', value: 'modified' },
                    { label: '已支付', value: 'payed' },
                    { label: '已失效', value: 'inactive' },
                  ]}
                />
              </Form.Item>
            </Col>
            <Col span={4}>
              <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
                <Button type="primary" htmlType='submit'>查询</Button>
                <Button style={{ marginLeft: 8 }} htmlType='reset'>重置</Button>
              </Form.Item>
            </Col>
          </Row>
        </Form>
        <div className={styles.table}>
          <div className={styles.bar}>
            <Button disabled={!selectedRows.length} type="primary" onClick={() => setVisible(true)}>
              批量结算
            </Button>
          </div>
          <Table
            rowKey="id"
            columns={columns}
            dataSource={datasource}
            rowSelection={{
              fixed: true,
              selectedRowKeys: selectedRows.map(item => item.id),
              onChange: onRowSelectChange,
              getCheckboxProps: (record) => ({
                disabled: datasource.filter(item => item.status === 'payed').map(item => item.id).includes(record.id)
              }),
            }}
            pagination={{
              total,
              onChange: onPaginationChange,
              showTotal: (total) => `共 ${total} 条`,
            }}
          />
        </div>
      </Spin>

      <Modal
        open={visible}
        title="确认结算以下账单？"
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
        <div className={styles.totalCount}>
          {
            totalCount.length ? (
              totalCount.map(([currency, count]) => (
                <Text strong key={currency}>
                  共计 {currency}: {(count as number).toFixed(2)}
                </Text>
              ))
            ) : null
          }
          <Input.TextArea
            onChange={(e) => setRemark(e.target.value)}
            style={{ margin: '8px 0px 4px' }}
            placeholder="请输入结算备注"
          />
        </div>
        <div className={styles.confirm}>
          {
            selectedRows.map(item => (
              <p key={item.id}>
                <span>{item.bank}</span> -
                <span>{item.card_last4}</span> -
                <span>{item.trade_date}</span> -
                <span>{`¥ ${item.amount_cny}` || `${item.currency} ${item.amount_foreign}`}</span>
              </p>
            ))
          }
        </div>
      </Modal>
    </div>
  );
}
