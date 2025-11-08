import { AppShell } from "@/components/shell/AppShell"
import HomePage from "@/components/pages/HomePage"

export default function Home() {
  return (
    <AppShell activeTab="home">
      <HomePage />
    </AppShell>
  )
}
