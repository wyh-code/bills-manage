import { useEffect, useState } from 'react';
import { Table, Form, Select, Row, Col, DatePicker, Button } from 'antd';
import { getColumns } from './getColumns'
import styles from './index.module.less';

function Summary() {
  const [datasource, setDatasource] = useState([]);
  const [cardOptions, setCardOptions] = useState([]);

  const fetchDatasource = () => {
    console.log('fetchDatasource')
  }

  const columns = getColumns() as any;

  useEffect(() => {
    fetchDatasource()
  }, [])

  return (
    <div className={styles.summary}>
      <Form
        className={styles.form}
      >
        <Row gutter={24}>
          <Col span={8}>
            <Form.Item label="卡号" style={{ marginBottom: 0 }}>
              <Select options={cardOptions} />
            </Form.Item>
          </Col>
          <Col span={8}>
            <Form.Item label="日期" style={{ marginBottom: 0 }}>
              <DatePicker.RangePicker style={{ width: '100%' }} />
            </Form.Item>
          </Col>
          <Col span={8}>
            <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
              <Button type="primary">查询</Button>
              <Button style={{ marginLeft: 8 }}>重置</Button>
            </Form.Item>
          </Col>
        </Row>
      </Form>
      <Table className={styles.table} columns={columns} dataSource={datasource} />
    </div>
  );
}

export default Summary;
