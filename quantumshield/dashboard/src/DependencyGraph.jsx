import { useMemo } from 'react'
import { ReactFlow, Background, Controls, MarkerType } from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import cbomData from './cbom_report.json'


const RISK_COLORS = {
  Critical: '#dc2626',
  High: '#ea580c',
  Medium: '#ca8a04',
  Low: '#16a34a',
}

function buildGraph() {
  const nodes = []
  const edges = []
  const vendorNodesAdded = new Set()
  const dataTypeNodesAdded = new Set()

  let serviceIndex = 0
  const serviceCount = Object.keys(cbomData.services).length

  Object.entries(cbomData.services).forEach(([serviceName, serviceData]) => {
    const context = serviceData.business_context || {}
    const risk = serviceData.risk_assessment || {}
    const riskColor = RISK_COLORS[risk.risk_level] || '#6b7280'

    const serviceX = 350
    const serviceY = serviceIndex * 160 + 40

    // Service node (the app itself)
    nodes.push({
      id: `service-${serviceName}`,
      position: { x: serviceX, y: serviceY },
      data: { label: `${serviceName}\n(${risk.risk_level || 'Unknown'})` },
      style: {
        background: riskColor,
        color: 'white',
        borderRadius: 10,
        padding: 10,
        fontWeight: 600,
        fontSize: 13,
        width: 190,
        textAlign: 'center',
        whiteSpace: 'pre-line',
        border: 'none',
      },
    })

    // Vendor nodes (to the left)
    const vendors = context.vendor_dependencies || []
    vendors.forEach((vendor, i) => {
      const vendorName = vendor.name
      if (!vendorName || vendorName === 'none') return

      const vendorId = `vendor-${vendorName}`
      if (!vendorNodesAdded.has(vendorId)) {
        vendorNodesAdded.add(vendorId)
        nodes.push({
          id: vendorId,
          position: { x: 40, y: serviceY + i * 60 },
          data: { label: `🏢 ${vendorName}` },
          style: {
            background: '#1e293b',
            color: '#e2e8f0',
            border: '1px solid #475569',
            borderRadius: 8,
            padding: 8,
            fontSize: 12,
            width: 170,
          },
        })
      }

      edges.push({
        id: `edge-${vendorId}-${serviceName}`,
        source: vendorId,
        target: `service-${serviceName}`,
        animated: !vendor.quantum_safe_roadmap_confirmed,
        style: { stroke: vendor.quantum_safe_roadmap_confirmed ? '#16a34a' : '#dc2626' },
        markerEnd: { type: MarkerType.ArrowClosed },
        label: vendor.quantum_safe_roadmap_confirmed ? 'PQC ready' : 'PQC unconfirmed',
        labelStyle: { fontSize: 10, fill: '#94a3b8' },
      })
    })

    // Data type nodes (to the right)
    const dataTypes = context.data_types || []
    dataTypes.forEach((dataType, i) => {
      const dataTypeId = `data-${dataType}`
      if (!dataTypeNodesAdded.has(dataTypeId)) {
        dataTypeNodesAdded.add(dataTypeId)
        nodes.push({
          id: dataTypeId,
          position: { x: 660, y: serviceY + i * 45 },
          data: { label: `📄 ${dataType}` },
          style: {
            background: '#312e81',
            color: '#e0e7ff',
            border: '1px solid #4338ca',
            borderRadius: 8,
            padding: 8,
            fontSize: 12,
            width: 170,
          },
        })
      }

      edges.push({
        id: `edge-${serviceName}-${dataTypeId}`,
        source: `service-${serviceName}`,
        target: dataTypeId,
        style: { stroke: '#64748b' },
        markerEnd: { type: MarkerType.ArrowClosed },
      })
    })

    serviceIndex += 1
  })

  return { nodes, edges }
}

function DependencyGraph() {
  const { nodes, edges } = useMemo(() => buildGraph(), [])

  return (
    <div style={{ height: '650px', background: '#0f172a', borderRadius: 12, border: '1px solid #334155' }}>
      <ReactFlow nodes={nodes} edges={edges} fitView>
        <Background color="#334155" gap={20} />
        <Controls />
      </ReactFlow>
    </div>
  )
}

export default DependencyGraph