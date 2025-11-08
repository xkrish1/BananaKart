import { AppShell } from "@/components/shell/AppShell"
import ExplorePage from "@/components/pages/ExplorePage"

export default function Explore() {
  return (
    <AppShell activeTab="explore">
      <ExplorePage />
    </AppShell>
  )
}
