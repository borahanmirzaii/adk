'use client'

export function ServiceStatus() {
  const services = [
    { name: 'Supabase', status: 'healthy' },
    { name: 'Redis', status: 'healthy' },
    { name: 'n8n', status: 'healthy' },
    { name: 'Langfuse', status: 'healthy' },
  ]

  return (
    <div className="p-4 border rounded-lg bg-white">
      <h3 className="font-semibold mb-2">Service Status</h3>
      <div className="space-y-2">
        {services.map((service) => (
          <div key={service.name} className="flex items-center justify-between text-sm">
            <span>{service.name}</span>
            <span
              className={`px-2 py-1 rounded ${
                service.status === 'healthy'
                  ? 'bg-green-100 text-green-800'
                  : 'bg-red-100 text-red-800'
              }`}
            >
              {service.status}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}

