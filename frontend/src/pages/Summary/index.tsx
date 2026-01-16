import { useState, useMemo, useCallback, useEffect } from 'react';
import { Table, Tooltip, InputNumber, Space, Typography, Spin, DatePicker, Select, Button, Form, Row, Col, message } from 'antd';
import { billApi } from '@/api/bill';
import { workspaceApi } from '@/api/workspace';
import dayjs from 'dayjs';
import AmountCell from './AmountCell';
import styles from './index.module.less';

const { Text } = Typography;
const { RangePicker } = DatePicker;

export default () => {
  const [exchangeRate, setExchangeRate] = useState(7.1);
  const [loading, setLoading] = useState(false);
  const [rawData, setRawData] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [workspaceList, setWorkspaceList] = useState<any[]>([]);
  const [cardOptions, setCardOptions] = useState<any[]>([]);
  const [form] = Form.useForm();

  // 筛选条件
  const [filters, setFilters] = useState<any>({
    dateRange: null,
    workspaceIds: [],
    cardNumbers: [],
    status: [],
  });

  // 获取空间列表
  const fetchWorkspaces = useCallback(async () => {
    try {
      const res = await workspaceApi.list({ status: 'active', role: 'viewer' });
      setWorkspaceList(res || []);
    } catch (error: any) {
      message.error(error.message || '获取空间列表失败');
    }
  }, []);

  // 获取卡号列表
  const fetchCardList = useCallback(async (workspaceIds?: string[]) => {
    try {
      const cards = await billApi.getCardList(workspaceIds);
      setCardOptions(cards);
    } catch (error: any) {
      message.error(error.message || '获取卡号列表失败');
    }
  }, []);

  // 获取账单列表
  const fetchBillList = useCallback(async () => {
    setLoading(true);
    try {
      const { dateRange, workspaceIds, cardNumbers, status } = filters;

      const params: any = {
        page: 1,
        page_size: 9999,
      };

      if (workspaceIds && workspaceIds.length > 0) {
        params.workspace_ids = workspaceIds;
      }

      if (cardNumbers && cardNumbers.length > 0) {
        params.card_last4_list = cardNumbers;
      }

      if (status && status.length > 0) {
        params.status_list = status;
      }

      if (dateRange && dateRange.length === 2) {
        params.start_date = dateRange[0].format('YYYY-MM-DD');
        params.end_date = dateRange[1].format('YYYY-MM-DD');
      }

      const result = await billApi.list(params);
      setRawData(result.items || []);
      setTotal(result.total || 0);
    } catch (error: any) {
      message.error(error.message || '获取账单列表失败');
      setRawData([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchWorkspaces();
    fetchCardList();
  }, []);

  useEffect(() => {
    fetchBillList();
  }, [fetchBillList]);

  // 数据处理逻辑
  const { tableData, sortedMonths, totalCount, monthTotals } = useMemo(() => {
    const cardMap = new Map();
    const monthSet = new Set();
    const monthTotals: any = {};

    // 按卡号分组并计算每月汇总
    rawData.forEach((bill) => {
      const {
        bank,
        card_last4,
        amount_foreign,
        amount_cny,
        currency,
        trade_date,
        raw_line,
        description,
        file_upload_id,
        workspace_id
      } = bill;

      const month = dayjs(trade_date).format('YYYY-MM');
      const cardKey = `${card_last4}_${bank}`;

      monthSet.add(month);

      // 初始化月份合计
      if (!monthTotals[month]) {
        monthTotals[month] = {};
      }

      // 若账单中包含人民币（即银行已自动转换汇率）则取账单中的人民币金额
      if (amount_cny) {
        monthTotals[month].CNY = monthTotals[month].CNY || 0;
        monthTotals[month].CNY += amount_cny;
      } else {
        monthTotals[month][currency] = monthTotals[month][currency] || 0;
        monthTotals[month][currency] += amount_foreign
      }

      if (!cardMap.has(cardKey)) {
        cardMap.set(cardKey, {
          bank,
          card_last4,
          monthlyData: {}
        });
      }

      const { monthlyData } = cardMap.get(cardKey);
      if (!monthlyData[month]) {
        monthlyData[month] = {
          originalDataList: [],
          currencyAmounts: {}, // 按币种分别存储
        };
      }

      monthlyData[month].originalDataList.push({
        raw_line: raw_line || description,
        origin: {
          file_upload_id,
          workspace_id,
          amount_foreign,
          amount_cny,
          currency,
          trade_date,
        }
      });

      // 按币种累计
      if (amount_cny) {
        monthlyData[month].currencyAmounts.CNY = monthlyData[month].currencyAmounts.CNY || 0;
        monthlyData[month].currencyAmounts.CNY += (amount_cny || 0);
      } else {
        monthlyData[month].currencyAmounts[currency] = monthlyData[month].currencyAmounts[currency] || 0;
        monthlyData[month].currencyAmounts[currency] += (amount_foreign || 0);
      }
    });

    const sortedMonths = Array.from(monthSet).sort();

    // 转换为表格数据
    let totalCount = [];
    const tableData = Array.from(cardMap.values()).map(({ bank, card_last4, monthlyData }) => {
      const row: any = {
        key: `${card_last4}_${bank}`,
        cardNumber: card_last4,
        bank: bank,
        rowCount: {},
      };

      sortedMonths.forEach((month: string) => {
        row[month] = monthlyData[month] || null;
        if (monthlyData[month]) {
          Object.keys(monthlyData[month].currencyAmounts).forEach(currency => {
            row.rowCount[currency] = row.rowCount[currency] || 0;
            row.rowCount[currency] += monthlyData[month].currencyAmounts[currency];
          })
        }
      });

      totalCount.push(row.rowCount);
      return row;
    });

    return { tableData, sortedMonths, totalCount, monthTotals };
  }, [rawData]);

  // 处理筛选
  const handleFilter = (values: any) => {
    setFilters({
      dateRange: values.dateRange || null,
      workspaceIds: values.workspaceIds || [],
      cardNumbers: values.cardNumbers || [],
      status: values.status || [],
    });
  };

  // 重置筛选
  const handleReset = () => {
    form.resetFields();
    setFilters({
      dateRange: null,
      workspaceIds: [],
      cardNumbers: [],
      status: [],
    });
  };

  // 空间变化时重新获取卡号列表
  const handleWorkspaceChange = (workspaceIds: string[]) => {
    fetchCardList(workspaceIds);
    form.setFieldsValue({ cardNumbers: [] }); // 清空卡号选择
  };

  // 构建表格列
  const columns: any = useMemo(() => {
    const baseColumns = [
      {
        title: '银行卡信息',
        dataIndex: 'info',
        key: 'info',
        fixed: 'left',
        width: 200,
        render: (_: any, { bank, cardNumber }: any) => (
          <Text strong>
            {bank} - {cardNumber}
          </Text>
        ),
      },
      {
        title: '合计',
        dataIndex: 'rowCount',
        key: 'rowCount',
        fixed: 'left',
        width: 120,
        render: (rowCount: number, index) => (
          Object.keys(rowCount).map(currency => (
            <p key={index}><Text strong>{currency}: {rowCount[currency].toFixed(2)}</Text></p>
          ))
        ),
      },
    ];

    const monthColumns = sortedMonths.map((month: string) => ({
      title: () => {
        const totals = monthTotals[month] || {};
        const currencyItems = Object.entries(totals)
          .map(([currency, amount]) => (
            <div key={currency}>
              {currency}: {(amount as number).toFixed(2)}
            </div>
          ));

        const tooltipContent = (
          <div>
            <div style={{ marginBottom: 4, fontWeight: 'bold' }}>{month}</div>
            {currencyItems}
          </div>
        );

        return (
          <Tooltip title={tooltipContent} placement="topLeft">
            <div>{month}</div>
          </Tooltip>
        );
      },
      dataIndex: month,
      key: month,
      width: 150,
      align: 'right',
      render: (_: any, row: any) => <AmountCell month={month} row={row} />,
    }));

    return [...baseColumns, ...monthColumns];
  }, [sortedMonths, monthTotals, exchangeRate]);

  const plusTotalCount = (totalCount) => {
    const totalMap = {};
    totalCount.forEach(cardTotal => {
      Object.keys(cardTotal).forEach(currency => {
        totalMap[currency] = totalMap[currency] || 0;
        totalMap[currency] += cardTotal[currency]
      })
    })
    console.log(Object.entries(totalMap))
    return Object.entries(totalMap)
  }

  return (
    <div className={styles.summary}>
      <Spin spinning={loading}>
        <Form
          form={form}
          onFinish={handleFilter}
          onReset={handleReset}
          className={styles.form}
        >
          <Row gutter={30}>
            <Col span={5}>
              <Form.Item label="账务空间" name="workspaceIds" style={{ marginBottom: 0 }}>
                <Select
                  mode="multiple"
                  placeholder="请选择账务空间"
                  allowClear
                  onChange={handleWorkspaceChange}
                  maxTagCount="responsive"
                >
                  {workspaceList.map(ws => (
                    <Select.Option key={ws.id} value={ws.id}>
                      {ws.name}
                    </Select.Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={5}>
              <Form.Item label="卡号" name="cardNumbers" style={{ marginBottom: 0 }}>
                <Select
                  mode="multiple"
                  placeholder="请选择卡号"
                  allowClear
                  maxTagCount="responsive"
                >
                  {cardOptions.map(card => (
                    <Select.Option key={card.card_last4} value={card.card_last4}>
                      {card.card_last4} ({card.count})
                    </Select.Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={5}>
              <Form.Item label="日期" name="dateRange" style={{ marginBottom: 0 }}>
                <RangePicker style={{ width: '100%' }} format="YYYY-MM-DD" />
              </Form.Item>
            </Col>
            <Col span={5}>
              <Form.Item label="状态" name="status" style={{ marginBottom: 0 }}>
                <Select
                  mode="multiple"
                  placeholder="请选择状态"
                  options={[
                    // active/inactive/pending/modified/payed
                    { label: '待确定', value: 'pending' },
                    { label: '已确定', value: 'active' },
                    { label: '已修改', value: 'modified' },
                    { label: '已支付', value: 'payed' },
                    { label: '已失效', value: 'inactive' },
                  ]}
                />
              </Form.Item>
            </Col>
            <Col span={4}>
              <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
                <Button type="primary" htmlType="submit">查询</Button>
                <Button htmlType="reset" style={{ marginLeft: 8 }}>重置</Button>
              </Form.Item>
            </Col>
          </Row>
        </Form>

        <div className={styles.table}>
          <Space align="center" className={styles.bar}>
            <Text strong>汇率设置（USD to CNY）：</Text>
            <InputNumber
              value={exchangeRate}
              onChange={(value) => setExchangeRate(value || 7.1)}
              min={0}
              step={0.1}
              precision={2}
              className={styles.rate}
            />
            <span className={styles.barItem} style={{ marginLeft: 20 }}>
              <Text strong>总合计：</Text>
              {plusTotalCount(totalCount).map(([currency, count], index) => (
                <Text className={styles.itemText} style={{ marginLeft: 10 }} strong key={index}>
                  {currency} 
                  <span className={styles.count}>{(count as number).toFixed(2)}</span>
                </Text>
              ))}
            </span>
            <span style={{ marginLeft: 20 }}>
              <Text strong>共 {total} 项</Text>
            </span>
          </Space>
          <Table
            columns={columns}
            dataSource={tableData}
            scroll={{ x: 'max-content' }}
            pagination={false}
            bordered
            size="small"
          />
        </div>
      </Spin>
    </div>
  );
};