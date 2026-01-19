import React, { useState } from 'react';
import { Drawer } from 'antd';
import { FileSearchOutlined } from '@ant-design/icons';
import FilePreview from '@/component/FilePreview';

export default ({ children, style, fileId, workspaceId }: any) => {
  const [visible, setVisible] = useState(false);

  return (
    <div style={style}>
      {children ? (
        React.cloneElement(children, { onClick: () => setVisible(true) })
      ) : (
        <FileSearchOutlined onClick={() => setVisible(true)} />
      )}
      <Drawer
        open={visible}
        title="原始账单"
        onClose={() => setVisible(false)}
        size={1200}
      >
        <FilePreview
          fileId={fileId}
          workspaceId={workspaceId}
        />
      </Drawer>
    </div>
  )
}

