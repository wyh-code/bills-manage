import React, { useEffect, useState } from 'react';
import * as XLSX from 'xlsx';
import { Tabs, Spin, Alert } from 'antd';
import styles from './index.module.less';

interface ExcelViewProps {
  file: File;
}

interface SheetData {
  [key: string]: any[][];
}

const ExcelView: React.FC<ExcelViewProps> = ({ file }) => {
  const [sheets, setSheets] = useState<SheetData>({});
  const [sheetNames, setSheetNames] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadExcel();
  }, [file]);

  const loadExcel = async () => {
    try {
      setLoading(true);
      setError(null);

      const arrayBuffer = await file.arrayBuffer();
      const workbook = XLSX.read(arrayBuffer, { type: 'array' });

      const sheetsData: SheetData = {};
      const names: string[] = [];

      workbook.SheetNames.forEach((sheetName) => {
        const worksheet = workbook.Sheets[sheetName];
        const jsonData = XLSX.utils.sheet_to_json(worksheet, {
          header: 1,
          defval: '',
          raw: false,
        }) as any[][];

        sheetsData[sheetName] = jsonData;
        names.push(sheetName);
      });

      setSheets(sheetsData);
      setSheetNames(names);
      setLoading(false);
    } catch (err) {
      console.error('解析 Excel 失败:', err);
      setError('无法解析 Excel 文件，请确保文件格式正确');
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className={styles.loading}>
        <Spin size="large" tip="正在加载 Excel 文件..." />
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

  if (sheetNames.length === 0) {
    return (
      <div className={styles.empty}>
        <Alert message="文件为空" description="该 Excel 文件没有数据" type="warning" showIcon />
      </div>
    );
  }

  const tabItems = sheetNames.map((name) => ({
    key: name,
    label: name,
    children: (
      <div className={styles.tableWrapper}>
        <table className={styles.excelTable}>
          <tbody>
            {sheets[name]?.map((row, rowIndex) => (
              <tr key={rowIndex}>
                {row.map((cell, cellIndex) => (
                  <td key={cellIndex} className={rowIndex === 0 ? styles.headerCell : ''}>
                    {cell || ''}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    ),
  }));

  return (
    <div className={styles.excelView}>
      <div className={styles.info}>
        <span>文件名: {file.name}</span>
        <span>大小: {(file.size / 1024).toFixed(2)} KB</span>
      </div>
      <Tabs items={tabItems} />
    </div>
  );
};

export default ExcelView;
