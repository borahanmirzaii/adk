'use client'

export function MetricsCard() {
  return (
    <div className="p-4 border rounded-lg bg-white">
      <h3 className="font-semibold mb-2">System Metrics</h3>
      <div className="space-y-2 text-sm">
        <div className="flex justify-between">
          <span>CPU Usage:</span>
          <span>45%</span>
        </div>
        <div className="flex justify-between">
          <span>Memory:</span>
          <span>62%</span>
        </div>
        <div className="flex justify-between">
          <span>Disk:</span>
          <span>38%</span>
        </div>
      </div>
    </div>
  )
}

