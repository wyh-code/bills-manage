import React, { useEffect, useState } from 'react';
import { Spin, Alert } from 'antd';
import { fileApi } from '@/api/upload';
import PDFViewer from '@/component/PDFViewer';
import ExcelView from '@/component/ExcelView';
import styles from './index.module.less';

interface FilePreviewProps {
  fileId: string;
  workspaceId: string;
}

const FilePreview: React.FC<FilePreviewProps> = ({ fileId, workspaceId }) => {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  if(!fileId || !workspaceId) return null;

  useEffect(() => {
    loadFile();
  }, [fileId, workspaceId]);

  const loadFile = async () => {
    try {
      setLoading(true);
      setError(null);
      const fileObj = await fileApi.getFileForPreview(fileId, workspaceId);
      setFile(fileObj);
      setLoading(false);
    } catch (err) {
      console.error('加载文件失败:', err);
      setError(err instanceof Error ? err.message : '加载文件失败');
      setLoading(false);
    }
  };

  const getFileExtension = (filename: string): string => {
    return filename.split('.').pop()?.toLowerCase() || '';
  };

  const renderPreview = () => {
    if (!file) return null;
    const ext = getFileExtension(file.name);

    switch (ext) {
      case 'pdf':
        return <PDFViewer file={file} />;

      case 'xlsx':
      case 'xls':
      case 'csv':
        return file ? <ExcelView file={file} /> : null;

      case 'png':
      case 'jpg':
      case 'jpeg':
      case 'gif':
        return (
          <div className={styles.imagePreview}>
            <img src={URL.createObjectURL(file)} alt="预览图片" />
          </div>
        );

      case 'ecxml':
      case 'xml':
        return (
          <Alert
            message="XML 预览"
            description="XML 文件预览功能开发中，请下载后查看"
            type="info"
            showIcon
            action={
              <a onClick={() => fileApi.download(fileId, workspaceId)}>下载文件</a>
            }
          />
        );

      default:
        return (
          <Alert
            message="不支持预览"
            description={`暂不支持预览 .${ext} 格式的文件`}
            type="warning"
            showIcon
            action={
              <a onClick={() => fileApi.download(fileId, workspaceId)}>下载文件</a>
            }
          />
        );
    }
  };

  if (loading) {
    return (
      <div className={styles.loading}>
        <Spin size="large" tip="正在加载文件..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.error}>
        <Alert message="加载失败" description={error} type="error" showIcon />
      </div>
    );
  }

  return <div className={styles.filePreview}>{renderPreview()}</div>;
};

export default FilePreview;