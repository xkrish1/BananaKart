"use client"

import { ThemeProvider } from "@/context/ThemeContext"
import { BananakartProvider } from "@/context/BananakartContext"
import { Header } from "./Header"
import type { ReactNode } from "react"

function AppShellContent({ children, activeTab }: { children: ReactNode; activeTab: string }) {
  return (
    <div className="flex flex-col min-h-screen bg-background text-foreground">
      <Header activeTab={activeTab} />

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">{children}</main>
    </div>
  )
}

export function AppShell({ children, activeTab = "home" }: { children: ReactNode; activeTab: string }) {
  return (
    <ThemeProvider>
      <BananakartProvider>
        <AppShellContent activeTab={activeTab}>{children}</AppShellContent>
      </BananakartProvider>
    </ThemeProvider>
  )
}
