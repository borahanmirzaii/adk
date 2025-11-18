'use client'

import { CopilotKit } from '@copilotkit/react-core'
import { CopilotSidebar } from '@copilotkit/react-ui'
import '@copilotkit/react-ui/styles.css'

export function CopilotKitProvider({ children }: { children: React.ReactNode }) {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
  
  return (
    <CopilotKit runtimeUrl={`${apiUrl}/api/copilotkit`}>
      <CopilotSidebar>
        {children}
      </CopilotSidebar>
    </CopilotKit>
  )
}

