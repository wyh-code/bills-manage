import { useState } from 'react';
import { Button, Modal, Drawer } from 'antd';
import { FileSearchOutlined, EyeOutlined, CloudDownloadOutlined } from '@ant-design/icons';
import { fileApi } from '@/api/upload';
import FilePreview from '@/component/FilePreview';
import styles from './index.module.less';

export default ({ month, row }) => {
  const [open, setOpen] = useState(false);
  const [visible, setVisible] = useState(false);
  const [fileInfo, setFileInfo] = useState(null);

  const data = row[month]

  const onPriview = (fileInfo) => {
    setVisible(true);
    setFileInfo(fileInfo)
  }

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
            <p key={raw_line.raw_line} style={{ whiteSpace: 'nowrap' }}>
              {`${row.key}_`}
              {raw_line.origin.trade_date}: {raw_line.origin.amount_cny ?
                `CNY ${raw_line.origin.amount_cny}` :
                `${raw_line.origin.currency} ${raw_line.origin.amount_foreign}`}

                <FileSearchOutlined 
                  style={{ marginLeft: 10 }} 
                  onClick={() => onPriview(raw_line.origin)} 
                />
                <CloudDownloadOutlined 
                  style={{ marginLeft: 10 }} 
                  onClick={() => fileApi.download(raw_line.origin?.file_upload_id, raw_line.origin?.workspace_id)}
                />
            </p>
          ))
        }
      </Modal>
      <Drawer 
        open={visible} 
        title="原始账单" 
        onClose={() => setVisible(false)}
        size={1200}
      >
        <FilePreview
          fileId={fileInfo?.file_upload_id}
          workspaceId={fileInfo?.workspace_id}
        />
      </Drawer>
    </>
  )
}