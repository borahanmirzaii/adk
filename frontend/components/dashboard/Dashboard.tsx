'use client'

import { MetricsCard } from './MetricsCard'
import { ServiceStatus } from './ServiceStatus'
import { RecentActivity } from './RecentActivity'

export function Dashboard() {
  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">Dashboard</h2>
      <MetricsCard />
      <ServiceStatus />
      <RecentActivity />
    </div>
  )
}

