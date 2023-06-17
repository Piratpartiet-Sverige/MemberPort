import React, {
  useEffect,
  useRef,
  useState
} from 'react'
import classNames from 'classnames'
import { sendHealthRequest } from '@memberport/utils/api'
import type { OrgData } from '@memberport/utils/organization/orgdata'
import type { GeoData } from '@memberport/utils/geography/geodata'

interface AdminViewProps {
  id?: string
  className?: string
}

interface MailServer {
  url: string
  port: number
}

interface KratosStatus {
  identitiesCount: number
  status: string
}

interface RabbitMQStatus {
  url: string
  monitorUrl: string
  productName: string
  productVersion: string
  status: string
  clusterName: string
}

interface QueueTotals {
  messages: number
  rate: number
  ready: number
  unacknowledged: number
}

interface QueueChurnRate {
  connectionCreated: number
  connectionClosed: number
}

interface QueueMessageStats {
  ack: number
  get: number
  publish: number
  redeliver: number
  unroutable: number
}

export const AdminView: React.FC<AdminViewProps> = (props) => {
  const {
    id = 'admin-view',
    className
  } = props

  const [defaultCountry, setDefaultCountry] = useState<GeoData | null>(null)
  const [defaultOrg, setDefaultOrg] = useState<OrgData | null>(null)
  const [kratosStatus, setKratosStatus] = useState<KratosStatus | null>(null)
  const [mailServer, setMailServer] = useState<MailServer | null>(null)
  const [queueStatus, setQueueStatus] = useState<RabbitMQStatus | null>(null)
  const [queueTotals, setQueueTotals] = useState<QueueTotals | null>(null)
  const [queueChurnRate, setQueueChurnRate] = useState<QueueChurnRate | null>(null)
  const [queueMessageStats, setQueueMessageStats] = useState<QueueMessageStats | null>(null)

  const timeoutRef = useRef<NodeJS.Timeout | null>(null)

  function checkHealth (): void {
    sendHealthRequest()
      .then(async (response) => {
        const respJson = await response.json()
        console.log(respJson)

        setDefaultCountry(respJson.data.general.default_country)
        setDefaultOrg(respJson.data.general.default_org)
        setKratosStatus({
          status: respJson.data.kratos.status,
          identitiesCount: Number(respJson.data.kratos.identity_count)
        })
        setMailServer({
          url: respJson.data.general.smtp_url,
          port: Number(respJson.data.general.smtp_port)
        })
        setQueueStatus({
          url: respJson.data.queue.broker_url,
          monitorUrl: respJson.data.queue.monitor_url,
          productName: respJson.data.queue.product_name,
          productVersion: respJson.data.queue.product_version,
          status: respJson.data.message,
          clusterName: respJson.data.queue.cluster_name
        })
        setQueueTotals({
          messages: Number(respJson.data.queue.queue_totals.messages),
          rate: Number(respJson.data.queue.queue_totals.messages_details.rate),
          ready: Number(respJson.data.queue.queue_totals.messages_ready),
          unacknowledged: Number(respJson.data.queue.queue_totals.messages_unacknowledged)
        })
        setQueueChurnRate({
          connectionCreated: Number(respJson.data.queue.churn_rates.connection_created),
          connectionClosed: Number(respJson.data.queue.churn_rates.connection_closed)
        })
        setQueueMessageStats({
          ack: Number(respJson.data.queue.message_stats.ack),
          get: Number(respJson.data.queue.message_stats.get),
          publish: Number(respJson.data.queue.message_stats.publish),
          redeliver: Number(respJson.data.queue.message_stats.redeliver),
          unroutable: Number(respJson.data.queue.message_stats.drop_unroutable)
        })
      })
      .catch(err => {
        console.warn(err)
      })
  }

  useEffect(() => {
    checkHealth()
    return () => {
      if (timeoutRef.current !== null) {
        clearTimeout(timeoutRef.current)
      }
    }
  }, [])

  return (
    <div
      id={id}
      className={classNames('columns', className)}
    >
      <div className="column">
        <div className="content">
          <h2>Globala inställningar</h2>
          <b>Huvudorganisation: </b>{defaultOrg?.name}
          <br />
          <b>Huvudland: </b>{defaultCountry?.name}
        </div>
      </div>
      <div className="column">
        <div className="content">
          <h2>Meddelandekö</h2>
          <b>Meddelande URL:</b> {queueStatus?.url}
          <br />
          <b>Översikts URL:</b> {queueStatus?.monitorUrl}
          <br />
          <b>Status:</b> {queueStatus?.status}
          <br />
          <h3>Detaljer</h3>

          <b>{queueStatus?.productName} version:</b> {queueStatus?.productVersion}
          <br />
          <b>Cluster name:</b> {queueStatus?.clusterName}
          <br />
          <b>Connections created:</b> {queueChurnRate?.connectionCreated}
          <br />
          <b>Connections closed:</b> {queueChurnRate?.connectionClosed}
          <br />
          <b>Messages:</b> {queueTotals?.messages}
          <br />
          <b>Messages rate:</b> {queueTotals?.rate}
          <br />
          <b>Messages ready:</b> {queueTotals?.ready}
          <br />
          <b>Messages unacknowledged:</b> {queueTotals?.unacknowledged}
          <br />
          <b>Ack totals:</b> {queueMessageStats?.ack}
          <br />
          <b>Get totals:</b> {queueMessageStats?.get}
          <br />
          <b>Publish totals:</b> {queueMessageStats?.publish}
          <br />
          <b>Redeliver totals:</b> {queueMessageStats?.redeliver}
          <br />
          <b>Drop unroutables:</b> {queueMessageStats?.unroutable}
        </div>
      </div>
      <div className="column">
        <div className="content">
          <h2>Mejlhantering</h2>
          <b>SMTP Server: </b>{mailServer?.url}
          <br />
          <b>SMTP Port: </b>{mailServer?.port}
        </div>
      </div>
      <div className="column">
        <div className="content">
          <h2>Kratos</h2>
          <b>Antal identiteter: </b>{kratosStatus?.identitiesCount.toString()}
          <br />
          <b>Status: </b>{kratosStatus?.status}
        </div>
      </div>
    </div>
  )
}

export default AdminView
