import { AppShell } from "@/components/shell/AppShell"
import DashboardPage from "@/components/pages/DashboardPage"

export default function Dashboard() {
  return (
    <AppShell activeTab="dashboard">
      <DashboardPage />
    </AppShell>
  )
}
