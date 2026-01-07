
import { useState } from "react";
import { Drawer } from "antd";
import { RightOutlined } from '@ant-design/icons';
import styles from './index.module.less';
import Empty from "@/component/Empty";

export default () => {
  const [open, setOpen] = useState(false)

  return (
    <div className={styles.costView}>
      <div className={styles.name} onClick={() => setOpen(true)}>
        <span>详情</span>
        <RightOutlined />
      </div>
      <Drawer
        size={800}
        title="历史账单"
        open={open}
        onClose={() => setOpen(false)}
      >
        <Empty style={{ margin: '30vh 0' }} />
      </Drawer>
    </div>
  )
}