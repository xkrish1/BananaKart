import { AppShell } from "@/components/shell/AppShell"
import MapPage from "@/components/pages/MapPage"

export default function Map() {
  return (
    <AppShell activeTab="map">
      <MapPage />
    </AppShell>
  )
}
