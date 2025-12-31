
import { useState } from 'react';
import { Form, Upload, UploadProps, message, Select } from 'antd';
import { isExcel, isImage, isPDF, getFileType } from '@/utils/utils';
import Empty from '@/component/Empty';
import PDFView from './PDFView';
import ExcelView from './ExcelView';
import styles from './index.module.less';

export default () => {
  const [loading, setUploading] = useState(false);
  const [file, setFile] = useState(null);

  const [form] = Form.useForm();

  const uploadProps: UploadProps = {
    name: 'file',
    multiple: true,
    showUploadList: false,
    accept: '.pdf,.png,.jpg,.jpeg,.xml,.xlsx',
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
        // const result = await uploadBill(file);
        // setUploadResult(result);
        // setModalVisible(true);

        // if (result.is_duplicate) {
        //   message.warning('文件已存在，返回已有数据');
        // } else {
        //   message.success('文件上传成功');
        // }
      } catch (error: any) {
        message.error(error.response?.data?.message || '上传失败');
      } finally {
        setUploading(false);
      }

      return false;
    },
  };

  return (
    <div className={styles.upload}>
      <div className={styles.conteiner}>
        <div className={styles.formConteiner}>
          <Form
            form={form}
            disabled={loading}
            className={styles.form}
            layout="vertical"
          >
            <Form.Item style={{ marginBottom: 0 }} label="账务空间" required rules={[{ required: true }]} name="workspace">
              <Select />
            </Form.Item>
          </Form>
          <Upload {...uploadProps} style={{ width: "100%" }}>
            <div className={styles.uploadInner}>
              支持 PDF、PNG、JPG、ECXML 格式，单个文件不超过 16MB
            </div>
          </Upload>
        </div>
        <div className={styles.dataView}>
          <div className={styles.title}>解析结果</div>
          <div className={styles.dataContent}>
            <Empty style={{ margin: '40px 0' }} />
          </div>
        </div>
      </div>
      <div className={styles.preview}>
        {
          file ? (
            <>
              {isPDF(file) ? <PDFView fileUrl={URL.createObjectURL(file)} /> : null}
              {isExcel(file) ? <ExcelView file={file} /> : null}
              {isImage(file) ? <img src={URL.createObjectURL(file)} /> : null}
            </>
          ) : <Empty style={{ margin: '30vh auto' }} />
        }
      </div>
    </div>
  );
}
