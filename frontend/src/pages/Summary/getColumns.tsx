
export const getColumns = () => {
  const columns = [
    {
      title: '发卡行',
      width: 100,
      dataIndex: 'bank',
      key: 'name',
      fixed: 'start',
    },
    {
      title: '卡号',
      width: 100,
      dataIndex: 'card',
      key: 'card',
      fixed: 'start',
    },
  ];

  return columns
}
