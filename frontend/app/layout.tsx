import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { CopilotKitProvider } from '@/components/CopilotKitProvider'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'ADK Dev Environment Manager',
  description: 'AI-powered development environment assistant',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <CopilotKitProvider>
          {children}
        </CopilotKitProvider>
      </body>
    </html>
  )
}

