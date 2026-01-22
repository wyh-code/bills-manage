/**
 * 文件类型判断工具
 */

import dayjs from 'dayjs';

// MIME 类型映射
const FILE_TYPES = {
  excel: [
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.ms-excel.sheet.macroEnabled.12',
    'text/csv',
    'application/csv',
  ],
  pdf: [
    'application/pdf',
  ],
  image: [
    'image/jpeg',
    'image/png',
    'image/gif',
    'image/bmp',
    'image/webp',
    'image/svg+xml',
  ],
};

// 文件扩展名映射
const FILE_EXTENSIONS = {
  excel: /\.(xlsx?|xlsm?|xlsb|ecxml|csv)$/i,
  pdf: /\.pdf$/i,
  image: /\.(jpe?g|png|gif|bmp|webp|svg)$/i,
};

/**
 * 判断是否为 Excel
 */
export const isExcel = (file: File): boolean => {
  return FILE_TYPES.excel.includes(file.type) ||
    FILE_EXTENSIONS.excel.test(file.name);
};

/**
 * 判断是否为 PDF
 */
export const isPDF = (file: File): boolean => {
  return FILE_TYPES.pdf.includes(file.type) ||
    FILE_EXTENSIONS.pdf.test(file.name);
};

/**
 * 判断是否为图片
 */
export const isImage = (file: File): boolean => {
  return FILE_TYPES.image.includes(file.type) ||
    FILE_EXTENSIONS.image.test(file.name);
};

/**
 * 获取文件类型
 */
export const getFileType = (file: File): 'excel' | 'pdf' | 'image' | 'unknown' => {
  if (isExcel(file)) return 'excel';
  if (isPDF(file)) return 'pdf';
  if (isImage(file)) return 'image';
  return 'unknown';
};

/**
 * 批量判断文件类型
 */
export const checkFileTypes = (files: File[]) => {
  return files.map(file => ({
    file,
    type: getFileType(file),
    isExcel: isExcel(file),
    isPDF: isPDF(file),
    isImage: isImage(file),
  }));
};

export const formateTime = (time: any, bool?) => {
  const formatStr = `YYYY-MM-DD${bool ? ' HH:mm:ss' : ''}`
  return dayjs(time).format(formatStr)
}

export const formateUser = (members: any) => {
  return members.filter(it => it).map(user => user?.nickname).join(', ')
}

export const getUrlParams = (key?: string, url: string = window.location.href): any => {
  try {
    const urlObj = new URL(url);
    const params = new URLSearchParams(urlObj.search);
    const result: Record<string, string | string[]> = {};

    // 遍历所有参数
    for (const [paramKey, value] of params.entries()) {
      // 如果参数已存在（重复参数），转换为数组
      if (paramKey in result) {
        const existingValue = result[paramKey];
        if (Array.isArray(existingValue)) {
          existingValue.push(value);
        } else {
          result[paramKey] = [existingValue, value];
        }
      } else {
        result[paramKey] = value;
      }
    }

    // 根据是否传入key返回不同的结果
    if (key !== undefined) {
      return result[key] || null;
    }

    return result;
  } catch (error) {
    console.error('解析URL失败:', error);
    // 根据不同的调用方式返回不同的默认值
    if (key !== undefined) {
      return null;
    }
    return {};
  }
}

export const getTotalCount = (list) => {
  const totalCount: any = {};
  list.forEach(row => {
    if (row.amount_cny) {
      totalCount.CNY = totalCount.CNY || 0;
      totalCount.CNY += row.amount_cny
    } else {
      totalCount[row.currency] = totalCount[row.currency] || 0;
      totalCount[row.currency] += row.amount_foreign
    }
  })
  return Object.entries(totalCount)
}


export const getMonthDaysArray = (dateStr) => {
  const [year, month] = dateStr.split('-').map(Number);
  
  // 获取当月第一天和最后一天的日期对象
  const firstDate = new Date(year, month - 1, 1); 
  const lastDate = new Date(year, month, 0); 
  
  // 计算当月有多少天
  const daysInMonth = lastDate.getDate();
  
  // 生成包含当月所有日期的数组
  const daysArray = [];
  
  for (let day = 1; day <= daysInMonth; day++) {
    // 格式化日期为 'YYYY-MM-DD'
    const formattedDate = `${year}-${month.toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}`;
    daysArray.push(formattedDate);
  }
  
  return daysArray;
}
