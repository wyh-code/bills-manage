import { useEffect, useState } from "react";
import { Button, Modal, Form, Input } from "antd";
import Empty from "@/component/Empty";
import styles from './index.module.less';
import Link from "@/component/Link";


export default () => {
  const [open, setOpen] = useState(false);
  const [workspaces, setWorkspaces] = useState([{}, {}, {}, {}, {}])

  const [form] = Form.useForm();

  const fetchWorkspace = () => {
    console.log('fetchWorkspace')
  }

  useEffect(() => {
    fetchWorkspace()
  }, [fetchWorkspace])

  const onCancel = () => {
    form.resetFields();
    setOpen(false);
  }

  const onFinish = async (values) => {
    console.log('onFinish: ', values)
  }
  const onFinishFailed = () => {
    console.log('onFinishFailed')
  }

  return (
    <div className={styles.workspace}>
      <div className={styles.bar}>
        <div className={styles.title}>账务空间</div>
        <Button type='primary' onClick={() => setOpen(true)}>创建空间</Button>
      </div>
      <div className={styles.content}>
        {
          workspaces.length ? (
            workspaces.map(item => (
              <div className={styles.card}>
                <div >
                  <div className={styles.title}>
                    <div className={styles.name}>空间名称</div>
                    <div className={`${styles.status} ${styles['status-green']}`}>空间状态</div>
                  </div>
                </div>
                <div className={styles.detail}>
                  <div className={styles.item}>
                    <div className={styles.label}>空间ID:</div>
                    <div className={styles.value}>123saisaisalksa</div>
                  </div>
                  <div className={styles.item}>
                    <div className={styles.label}>空间成员:</div>
                    <div className={styles.value}>空间成员</div>
                  </div>
                  <div className={styles.item}>
                    <div className={styles.label}>空间成员:</div>
                    <div className={styles.value}>创建时间</div>
                  </div>
                </div>
                <div className={styles.footer}>
                  <Link>编辑</Link>
                  <span className={styles.remove}>删除</span>
                </div>
              </div>
            ))
          ) : <Empty fontSize={14} iconSize={100} style={{ padding: 20, margin: '30px auto' }} />
        }
      </div>
      <Modal
        title="创建账务空间"
        open={open}
        onCancel={onCancel}
        footer={null}
      >
        <Form
          form={form}
          onFinish={onFinish}
          onFinishFailed={onFinishFailed}
          layout="vertical"
        >
          <Form.Item
            label="空间名称"
            style={{ marginTop: 20 }}
            name="name"
            rules={[{ required: true }]}
          >
            <Input placeholder="请输入空间名称" />
          </Form.Item>
          <Form.Item label="空间描述" name="description">
            <Input.TextArea placeholder="请输入空间描述" />
          </Form.Item>
          <Form.Item style={{ textAlign: 'right', marginBottom: 0 }}>
            <Button htmlType="submit" type="primary">提交</Button>
            <Button onClick={onCancel} style={{ marginLeft: 10 }}>取消</Button>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}