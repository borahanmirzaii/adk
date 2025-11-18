'use client'

import { useEffect, useState } from 'react'
import { supabase } from '@/lib/supabase'

interface AgentStatus {
  name: string
  healthy: boolean
}

export function useRealtimeUpdates() {
  const [agentStatus, setAgentStatus] = useState<AgentStatus[]>([])

  useEffect(() => {
    // Subscribe to agent_status changes
    const channel = supabase
      .channel('agent_status')
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'agent_status',
        },
        (payload) => {
          console.log('Agent status update:', payload)
          // Update agent status
        }
      )
      .subscribe()

    // Fetch initial agent status
    supabase
      .from('agent_status')
      .select('*')
      .then(({ data, error }) => {
        if (!error && data) {
          setAgentStatus(
            data.map((agent: any) => ({
              name: agent.agent_name,
              healthy: agent.status === 'running',
            }))
          )
        }
      })

    return () => {
      channel.unsubscribe()
    }
  }, [])

  return { agentStatus }
}

