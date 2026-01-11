import { useEffect, useState } from 'react';
import { Form, Upload, UploadProps, message, Select, Button } from 'antd';
import { UploadOutlined, ReloadOutlined } from '@ant-design/icons';
import { isExcel, isImage, isPDF } from '@/utils/utils';
import { workspaceApi } from "@/api/workspace";
import { fileApi } from "@/api/upload";
import Empty from '@/component/Empty';
import PDFViewer from '@/component/PDFViewer';
import ExcelView from '@/component/ExcelView';
import Bills from './Bills';

import styles from './index.module.less';

export default () => {
  const [loading, setUploading] = useState(false);
  const [workspaceId, setWorkspaceId] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [options, setOptions] = useState<any[]>([]);
  const [uploadResult, setUploadResult] = useState<any>({});
  const [disabledUpload, setDisabledUpload] = useState<any>(false);

  const [form] = Form.useForm();

  const uploadProps: UploadProps = {
    name: 'file',
    multiple: false,
    showUploadList: false,
    disabled: !workspaceId || loading,
    accept: '.pdf,.png,.jpg,.jpeg,.xml,.xlsx,.ecxml',
    beforeUpload: async (file) => {
      const isValidType = isExcel(file) || isImage(file) || isPDF(file);
      const isValidSize = file.size / 1024 / 1024 < 16;

      if (!isValidType) {
        message.error('只支持 PDF、PNG、JPG、ECXML 格式');
        return false;
      }

      if (!isValidSize) {
        message.error('文件大小不能超过 16MB');
        return false;
      }

      setUploading(true);
      setFile(file);

      try {
        const result = await fileApi.upload(workspaceId, file);
        console.log('上传结果:', result);

        setUploadResult(result);

        if (result.status === "duplicate") {
          message.warning('文件已存在，返回已有数据');
        } else {
          message.success('文件上传成功，正在解析...');
        }
      } catch (error: any) {
        console.error('上传失败:', error);
        message.error(error.response?.data?.message || '上传失败');
        setFile(null);
        setUploadResult({});
      } finally {
        setUploading(false);
      }

      return false;
    },
  };

  const fetchWorkspace = async () => {
    try {
      const res = await workspaceApi.list({ status: 'active', role: 'editor' });
      const options = res?.map(item => ({
        label: item.name,
        value: item.id
      })) || [];
      setOptions(options);

      // 如果只有一个workspace，自动选中
      if (options.length === 1) {
        form.setFieldsValue({ workspace: options[0].value });
        setWorkspaceId(options[0].value);
      }
    } catch (err: any) {
      message.error(err.message || '获取空间列表失败');
    }
  };

  const formChange = (value: string) => {
    setWorkspaceId(value);
    // 切换workspace时清空之前的上传结果
    setFile(null);
    setUploadResult({});
  };

  const handleReset = () => {
    setFile(null);
    setUploadResult({});
    form.resetFields();
    setWorkspaceId('');
  };

  useEffect(() => {
    fetchWorkspace();
  }, []);

  return (
    <div className={styles.upload}>
      <div className={styles.preview}>
        {file ? (
          <>
            {isPDF(file) && <PDFViewer file={file} />}
            {isExcel(file) && <ExcelView file={file} />}
            {isImage(file) && <img src={URL.createObjectURL(file)} alt="preview" />}
          </>
        ) : (
          <Empty style={{ margin: '30vh auto' }} description="暂无预览" />
        )}
      </div>
      <div className={styles.conteiner}>
        <div className={styles.formConteiner}>
          <Form
            form={form}
            disabled={loading}
            className={styles.form}
            layout="vertical"
          >
            <Form.Item
              style={{ marginBottom: 16 }}
              label={(
                <span>
                  账务空间
                  <span className={styles.labelTip}>
                    账务空间选择后才能上传文件
                  </span>
                </span>
              )}
              required
              rules={[{ required: true, message: '请选择账务空间' }]}
              name="workspace"
            >
              <Select
                disabled={disabledUpload}
                placeholder="请选择账务空间"
                options={options}
                allowClear
                onChange={formChange}
              />
            </Form.Item>
          </Form>

          <Upload {...uploadProps} style={{ width: "100%" }} disabled={disabledUpload}>
            <div className={styles.uploadInner}>
              <UploadOutlined style={{ fontSize: 24 }} />
              <div>支持 PDF、PNG、JPG、ECXML 格式，单个文件不超过 16MB</div>
            </div>
          </Upload>
        </div>
        <Bills
          workspaceId={workspaceId}
          uploadResult={uploadResult}
          file={file}
          handleReset={handleReset}
          setDisabledUpload={(bool) => setDisabledUpload(bool)}
        />
      </div>
    </div>
  );
};