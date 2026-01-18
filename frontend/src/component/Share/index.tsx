import { useState } from 'react';
import { Radio, message, Modal, Input, Button, Spin } from 'antd';
import { invitationApi } from '@/api/invitation';
import shared from '@/assets/share.svg';
import disabledShare from '@/assets/disabled-share.svg';
import styles from './index.module.less';

export default ({ disabled, className, workspaceId }: any) => {
  const [sharedOpen, setSharedOpen] = useState(false);
  const [sharedUrl, setSharedUrl] = useState('');
  const [radioValue, setRadioValue] = useState('');
  const [loading, setLoading] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(sharedUrl);
      message.success('复制成功');
    } catch {
      message.error('复制失败');
    }
  };

  const closeModal = () => {
    setSharedOpen(false);
    setSharedUrl('');
    setRadioValue('')
  }

  const onCreateShared = async (e) => {
    const role = e.target.value;
    setRadioValue(role)
    try {
      setLoading(true);
      const res = await invitationApi.create({
        type: 'workspace',
        workspace_id: workspaceId,
        role
      });
      setSharedUrl(res.share_url || '');
      message.success('邀请码创建成功')
    } catch (error: any) {
      message.error(error.message || '创建邀请失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div
        className={`${styles.shared} ${className} ${disabled && styles.disabled}`}
        onClick={() => setSharedOpen(true)}
      >
        {
          disabled ? (
            <img className="disabled" src={disabledShare} />
          ) : (
            <img className="active" src={shared} />
          )
        }
        <span>分享</span>
      </div>
      <Modal
        title="创建分享链接"
        closable={false}
        open={sharedOpen}
        footer={(
          <>
            {sharedUrl ? <Button type="primary" onClick={handleCopy}>复制</Button> : null}
            <Button onClick={closeModal} style={{ marginLeft: 10 }}>关闭</Button>
          </>
        )}
      >
        <div className={styles.radio}>
          <Radio.Group
            value={radioValue}
            onChange={onCreateShared}
            style={{ marginBottom: 10, marginRight: 30 }}
            options={[
              { value: 'editor', label: '可编辑' },
              { value: 'viewer', label: '可查看' }
            ]}
          />
        </div>
        <Spin spinning={loading}>
          <Input.TextArea
            disabled
            placeholder='请选择邀请链接权限'
            value={sharedUrl}
          />
        </Spin>
      </Modal>
    </>
  );
};