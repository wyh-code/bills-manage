import React, { useState } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import 'react-pdf/dist/Page/AnnotationLayer.css';  // ⭐ 添加
import 'react-pdf/dist/Page/TextLayer.css';        // ⭐ 添加
import styles from './index.module.less';

pdfjs.GlobalWorkerOptions.workerSrc = `https://unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;

interface PDFViewerAllProps {
  fileUrl: string;
}

const PDFViewerAll: React.FC<PDFViewerAllProps> = ({ fileUrl }) => {
  const [numPages, setNumPages] = useState<number>(0);
  const [scale, setScale] = useState<number>(1.0);

  const onDocumentLoadSuccess = ({ numPages }: { numPages: number }) => {
    setNumPages(numPages);
  };

  return (
    <div className={styles["pdf-viewer-all"]}>
      <div className={styles["pdf-toolbar"]}>
        <button onClick={() => setScale(s => Math.max(s - 0.2, 0.5))}>缩小</button>
        <span>{Math.round(scale * 100)}%</span>
        <button onClick={() => setScale(s => Math.min(s + 0.2, 3))}>放大</button>
      </div>

      <div className={styles["pdf-pages-container"]}>
        <Document
          file={fileUrl}
          onLoadSuccess={onDocumentLoadSuccess}
          loading={<div>加载中...</div>}
        >
          {Array.from(new Array(numPages), (_, index) => (
            <div key={`page_${index + 1}`} className={styles["pdf-page-wrapper"]}>
              <Page
                pageNumber={index + 1}
                scale={scale}
                renderTextLayer={false}
                renderAnnotationLayer={false}
              />
              <div className={styles["page-number"]}>第 {index + 1} 页</div>
            </div>
          ))}
        </Document>
      </div>
    </div>
  );
};

export default PDFViewerAll;
