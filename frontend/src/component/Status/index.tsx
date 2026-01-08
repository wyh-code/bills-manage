import styles from './index.module.less'

export default ({ type, style, statusMap={} }: any) => {

  const defaultMap = {
    active: '已确认',
    inactive: '已失效',
    pending: '待确认',
    payed: '已支付',
    ...statusMap
  }

  return (
    <span className={`${styles.status} ${styles[type]}`} style={style}>
      {defaultMap[type]}
    </span>
  )
}