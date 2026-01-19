import { useState } from 'react';
import { Button, Modal } from 'antd';
import { EyeOutlined, CloudDownloadOutlined } from '@ant-design/icons';
import { fileApi } from '@/api/upload';
import PreviewBill from '@/component/PreviewBill';
import styles from './index.module.less';

export default ({ month, row }) => {
  const [open, setOpen] = useState(false);

  const data = row[month]

  if (!data) return <span>--</span>;

  return (
    <>
      {
        Object.entries(data.currencyAmounts).map(([currency, amount]: [string, number], index) => (
          <div className={styles.amount} key={index}>
            {currency}: {amount.toFixed(2)}
            <EyeOutlined onClick={() => setOpen(true)} style={{ marginLeft: 8 }} />
          </div>
        ))
      }
      <Modal
        width={400}
        title={`${month}账单详情`}
        closable={false}
        open={open}
        footer={(
          <Button type="primary" onClick={() => setOpen(false)}>知道了</Button>
        )}
      >
        {
          data.originalDataList.map(raw_line => (
            <p key={raw_line.raw_line} style={{ whiteSpace: 'nowrap', display: 'flex' }}>
              {`${row.key}_`}
              {raw_line.origin.trade_date}: {raw_line.origin.amount_cny ?
                `CNY ${raw_line.origin.amount_cny}` :
                `${raw_line.origin.currency} ${raw_line.origin.amount_foreign}`}

              <PreviewBill
                style={{ marginLeft: 10 }}
                fileId={raw_line.origin.file_upload_id}
                workspaceId={raw_line.origin.workspace_id}
              />
              <CloudDownloadOutlined
                style={{ marginLeft: 10 }}
                onClick={() => fileApi.download(raw_line.origin?.file_upload_id, raw_line.origin?.workspace_id)}
              />
            </p>
          ))
        }
      </Modal>

    </>
  )
}