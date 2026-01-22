export const getUsed = (data) => {
  const config = {
    data,
    xField: 'day',
    yField: 'value',
    lineWidth: 20,
    label: {
      text: (d) => d.value ? `${(d.value).toFixed(2)}` : '',
      textBaseline: 'bottom',
    },
    axis: {
      x: {
        labelFormatter: (datum, index, data) => {
          let label = ''
          if (!index || index === data.length - 1) {
            label = datum.split('-').slice(1, 3).join('-')
          }
          return label
        }
      }
    },
    style: {
      // 圆角样式
      radiusTopLeft: 10,
      radiusTopRight: 10,
    },
  };

  return config;
}

export const getLineConfig = (data) => {
  const config = {
    data,
    xField: 'day',
    yField: 'value',
    point: {
      size: 5,
      shape: 'diamond',
    },
    interaction: {
      tooltip: {
        marker: false,
      },
    },
    label: {
      text: (d) => d.value ? d.value : '',
      textBaseline: 'bottom',
    },
    axis: {
      x: {
        labelAutoRotate: false, // 添加这一行
        labelFormatter: (datum, index, data) => {
          let label = ''
          if (!index || index === data.length - 1) {
            label = datum.split('-').slice(1, 3).join('-')
          }
          return label
        }
      }
    },
    style: {
      lineWidth: 2,
    },
  };

  return config;
}
