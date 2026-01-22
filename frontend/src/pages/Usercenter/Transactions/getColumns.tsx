import TextBallonWithEllipse from "@/component/TextBallonWithEllipse";
import { TOKEN_API_TYPE } from "@/utils/const";

export const getColumns = (type) => {

  const payColunms = [
    {
      dataIndex: 'id',
      title: '订单编号',
      width: '35%'
    },
    {
      dataIndex: 'amount',
      title: '金额',
      width: '25%'
    },
    {
      dataIndex: 'status',
      title: '状态',
      width: '15%'
    },
    {
      dataIndex: 'create_at',
      title: '创建时间',
      width: '25%'
    }
  ]

  const usedColunms = [
    {
      dataIndex: 'workspace_name',
      title: '账务空间',
      width: '10%',
      render: value => <TextBallonWithEllipse line={1} text={value} />
    },
    {
      dataIndex: 'original_filename',
      title: '账单文件',
      width: '20%',
      render: value => <TextBallonWithEllipse line={1} text={value} />
    },
    {
      dataIndex: 'api_type',
      title: '使用类型',
      width: '10%',
      render: value => TOKEN_API_TYPE[value]
    },
    {
      dataIndex: 'token_usage',
      title: 'token使用量',
      width: '12%'
    },
    {
      dataIndex: 'balance_before',
      title: '扣款前金额',
      width: '10%'
    },
    {
      dataIndex: 'balance_after',
      title: '扣款后金额',
      width: '10%'
    },
    {
      dataIndex: 'created_at',
      title: '创建时间',
      width: '15%',
    }
  ]

  return type == 'payed' ? payColunms : usedColunms;
}
