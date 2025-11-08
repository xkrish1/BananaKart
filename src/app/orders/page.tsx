import { AppShell } from "@/components/shell/AppShell"
import OrdersPage from "@/components/pages/OrdersPage"

export default function Orders() {
  return (
    <AppShell activeTab="home">
      <OrdersPage />
    </AppShell>
  )
}
