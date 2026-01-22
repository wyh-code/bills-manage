import { useEffect, useState } from 'react';
import { Segmented, Table } from 'antd';
import Empty from '@/component/Empty';
import { accountApi } from '@/api/account';
import { getColumns } from './getColumns';
import styles from './index.module.less'


export default () => {
  const [alignValue, setAlignValue] = useState('used');
  const [payDatasource, setPayDatasource] = useState<any>({});
  const [usedDatasource, setUsedDatasource] = useState<any>({});

  const columns = getColumns(alignValue);
  const datasource = alignValue === 'payed' ? payDatasource : usedDatasource;

  const getBillingRecords = async (page=1) => {
    try {
      const apis = {
        payed: '',
        used: 'getBillingRecords'
      }
      const usedDatasource = await accountApi[apis[alignValue]]({ page: 1, page_size: 10 })
      setUsedDatasource(usedDatasource)
    } catch (error) {
      console.error('账户余额获取失败:', error);
    }
  }

  useEffect(() => {
    getBillingRecords()
  }, [alignValue])

  return (
    <div className={styles.bills}>
      <div className={styles.pageName}>充值</div>
      <Segmented
        value={alignValue}
        style={{ marginBottom: 8 }}
        onChange={(value) => {
          setAlignValue(value);
        }}
        options={[{ label: "使用记录", value: 'used' }, { label: "充值记录", value: "payed" }]}
      />
      <div className={styles.table}>
        <Table
          columns={columns}
          dataSource={datasource?.items || []}
          pagination={{
            onChange: (page) => getBillingRecords(page),
            pageSize: datasource?.page_size || 10,
            className: datasource?.page || 1,
            total: datasource?.total || 1,
          }}
          locale={{
            emptyText: <Empty style={{ margin: '60px auto' }} />,
          }}
        />
      </div>
    </div>
  )
}
