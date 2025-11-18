export interface Agent {
  name: string
  status: string
  last_heartbeat?: string
  metrics?: Record<string, any>
}

export interface ChatMessage {
  user_message: string
  agent_response: string
  agent_name: string
  timestamp: string
}

export interface Session {
  session_id: string
  user_id: string
  messages: ChatMessage[]
}

