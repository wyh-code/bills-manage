import { useEffect, useState } from "react";
import { Button, Modal, Form, Input, message, Spin } from "antd";
import Empty from "@/component/Empty";
import styles from './index.module.less';
import Link from "@/component/Link";
import Share from "@/component/Share";
import TextBallonWithEllipse from "@/component/TextBallonWithEllipse";
import { WORKSTACE_STATUS } from '@/common/const';
import { workspaceApi, Workspace } from "@/api/workspace";
import authService from '@/auth/authService';
import { formateTime, formateUser } from '@/utils/utils'

export default ({ joined }) => {
  const [open, setOpen] = useState(false);
  const [formData, setData] = useState<any>({});
  const [spinning, setSpinning] = useState(false);
  const [workspaces, setWorkspaces] = useState([]);
  const user = authService.getUser();

  const [form] = Form.useForm();

  const fetchWorkspace = () => {
    workspaceApi.list().then(res => {
      setWorkspaces(res);
    }).catch((err: any) => {
      message.error(err.message)
    })
  }

  useEffect(() => {
    fetchWorkspace()
  }, [joined])

  const onCancel = () => {
    form.resetFields();
    setOpen(false);
  }

  const onFinish = async (values) => {
    setSpinning(true);
    if (!formData.id) {
      workspaceApi.create(values).then(res => {
        fetchWorkspace();
        setOpen(false);
      }).catch((error: any) => {
        message.error(error.message)
      }).finally(() => setSpinning(false))
    } else {
      updateWorkspace({ ...formData, ...values })
    }
  }
  const onFinishFailed = () => {
    console.log('onFinishFailed')
  }

  const updateWorkspace = (newWorkspace) => {
    workspaceApi.update(newWorkspace.id, newWorkspace).then(res => {
      fetchWorkspace();
      setOpen(false);
    }).catch((error: any) => {
      message.error(error.message)
    }).finally(() => setSpinning(false))
  }

  const onStatusChange = (workspace, status) => {
    if (status === 'active') {
      updateWorkspace({ ...workspace, status })
    } else {
      Modal.confirm({
        title: '确定冻结该空间吗？',
        content: '空间冻结后，该空间将不能新增账单上传！',
        onOk: () => {
          updateWorkspace({ ...workspace, status })
        }
      })
    }
  }

  const onEdit = (workspace) => {
    setOpen(true);
    setData(workspace);
    form.setFieldsValue(workspace)
  }

  const onDelete = (workspace) => {
    Modal.confirm({
      title: '确定删除该空间吗？',
      content: '空间删除后，空间下所有账单均不再参与数据计算！',
      onOk: () => {
        workspaceApi.delete(workspace.id).then(res => {
          fetchWorkspace();
          setOpen(false);
        }).catch((error: any) => {
          message.error(error.message)
        }).finally(() => setSpinning(false))
      }
    })
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
            workspaces.map((item: Workspace) => (
              <div className={styles.card} key={item.id}>
                <div className={`${item.status !== 'active' ? styles.greyInfo : ''}`}>
                  <div>
                    <div className={styles.title}>
                      <div className={styles.name}>
                        <TextBallonWithEllipse text={item.name} line={1} />
                        {/* {item.name} */}
                        </div>
                      <div
                        className={`${styles.status} ${item.status === 'active' ? styles['status-green'] : styles['status-grey']}`}
                      >
                        {console.log('item.status: ', item.status)}
                        {WORKSTACE_STATUS[item.status]}
                      </div>
                    </div>
                  </div>
                  <div className={styles.detail}>
                    {/* <div className={styles.item}>
                    <div className={styles.label}>空间ID:</div>
                    <div className={styles.value}>
                      <CopyText text={item.id} />
                    </div>
                  </div> */}
                    <div className={styles.item}>
                      <div className={styles.label}>负责人:</div>
                       <div className={styles.value}>
                        <TextBallonWithEllipse text={formateUser([item.owner])} line={1} />
                       </div>
                    </div>
                    <div className={styles.item}>
                      <div className={styles.label}>成员:</div>
                      <div className={styles.value}>
                        <TextBallonWithEllipse text={formateUser(item.members)} line={1} />
                      </div>
                    </div>
                    <div className={styles.item}>
                      <div className={styles.label}>描述:</div>
                      <div className={styles.value}>
                        <TextBallonWithEllipse text={item.description} line={1} />
                      </div>
                    </div>
                    <div className={styles.item}>
                      <div className={styles.label}>创建时间:</div>
                      <div className={styles.value}>{formateTime(item.created_at)}</div>
                    </div>
                  </div>
                </div>
                {/* 只有负责人可以操作 */}
                <div className={`${styles.footer} ${user.openid !== item.owner.openid ? styles.disabled : ''}`}>
                  <Share 
                    workspaceId={item.id}
                    className={`${item.status !== 'active' && styles.disabled}`} 
                    disabled={user.openid !== item.owner.openid || item.status !== 'active'} 
                  />
                  <div className={styles.right}>
                    <Link className={`${item.status !== 'active' && styles.disabled}`}  onClick={() => onEdit(item)}>编辑</Link>
                    {
                      item.status === 'active' ? (
                        <Link style={{ marginLeft: 8 }} onClick={() => onStatusChange(item, 'inactive')}>冻结</Link>
                      ) : (
                        <Link style={{ marginLeft: 8 }} onClick={() => onStatusChange(item, 'active')}>恢复</Link>
                      )
                    }
                    <Link 
                      className={`${item.status !== 'active' && styles.disabled}`}
                      type="red" 
                      style={{ marginLeft: 8 }} 
                      onClick={() => onDelete(item)}
                    >
                      删除
                    </Link>
                  </div>
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
        <Spin spinning={spinning}>
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
        </Spin>
      </Modal>
    </div>
  )
}