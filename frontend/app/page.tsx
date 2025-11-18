'use client'

import { ChatInterface } from '@/components/chat/ChatInterface'
import { Dashboard } from '@/components/dashboard/Dashboard'

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8">ADK Dev Environment Manager</h1>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <ChatInterface />
          </div>
          <div className="lg:col-span-1">
            <Dashboard />
          </div>
        </div>
      </div>
    </main>
  )
}

