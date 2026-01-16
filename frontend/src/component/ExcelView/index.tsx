import React, { useEffect, useState } from 'react';
import * as XLSX from 'xlsx';
import { Tabs, Spin, Alert } from 'antd';
import styles from './index.module.less';

interface ExcelViewProps {
  file: File;
}

interface SheetData {
  headers: string[];
  rows: any[][];
}

interface ParsedSheets {
  [sheetName: string]: SheetData;
}

const ExcelView: React.FC<ExcelViewProps> = ({ file }) => {
  const [sheets, setSheets] = useState<ParsedSheets>({});
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
      const workbook = XLSX.read(arrayBuffer, { 
        type: 'array',
        cellStyles: true,
        cellDates: true
      });

      const sheetsData: ParsedSheets = {};
      const names: string[] = [];

      workbook.SheetNames.forEach((sheetName) => {
        const worksheet = workbook.Sheets[sheetName];
        
        // 转换为二维数组,保留原始格式
        const jsonData = XLSX.utils.sheet_to_json(worksheet, {
          header: 1,
          defval: '',
          raw: false,
          dateNF: 'yyyy-mm-dd'
        }) as any[][];

        // 过滤空行
        const filteredData = jsonData.filter(row => 
          row.some(cell => cell !== null && cell !== undefined && cell !== '')
        );

        if (filteredData.length > 0) {
          // 第一行作为表头
          const headers = filteredData[0].map(cell => String(cell || ''));
          // 其余行作为数据
          const rows = filteredData.slice(1);

          sheetsData[sheetName] = { headers, rows };
          names.push(sheetName);
        }
      });

      setSheets(sheetsData);
      setSheetNames(names);
    } catch (err) {
      console.error('解析 Excel 失败:', err);
      setError('无法解析 Excel 文件，请确保文件格式正确');
    } finally {
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

  const tabItems = sheetNames.map((sheetName) => {
    const sheet = sheets[sheetName];
    
    return {
      key: sheetName,
      label: sheetName,
      children: (
        <div className={styles.tableWrapper}>
          <table className={styles.excelTable}>
            <thead>
              <tr>
                {sheet.headers.map((header, index) => (
                  <th key={index}>{header}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {sheet.rows.map((row, rowIndex) => (
                <tr key={rowIndex}>
                  {row.map((cell, cellIndex) => (
                    <td key={cellIndex}>{cell ?? ''}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ),
    };
  });

  return (
    <div className={styles.excelView}>
      <div className={styles.info}>
        <b>文件名: {file.name}</b>
        <span>大小: {(file.size / 1024).toFixed(2)} KB</span>
      </div>
      <Tabs items={tabItems} defaultActiveKey={sheetNames[0]} />
    </div>
  );
};

export default ExcelView;