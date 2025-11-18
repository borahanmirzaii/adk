'use client'

import { CopilotChat } from '@copilotkit/react-ui'
import { useRealtimeUpdates } from '@/hooks/useRealtimeUpdates'

export function ChatInterface() {
  const { agentStatus } = useRealtimeUpdates()

  return (
    <div className="flex flex-col h-[600px] border rounded-lg">
      <div className="p-4 border-b bg-gray-50">
        <h2 className="text-lg font-semibold">Dev Environment Assistant</h2>
        <div className="mt-2 flex gap-2">
          {agentStatus.map((agent) => (
            <span
              key={agent.name}
              className={`px-2 py-1 rounded text-sm ${
                agent.healthy ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
              }`}
            >
              ● {agent.name}
            </span>
          ))}
        </div>
      </div>
      <div className="flex-1 overflow-hidden">
        <CopilotChat
          labels={{
            title: 'Dev Environment Assistant',
            initial: 'Hi! I\'m monitoring your development environment. Ask me anything!',
          }}
          instructions="You are a helpful AI assistant managing the developer's environment."
        />
      </div>
    </div>
  )
}

