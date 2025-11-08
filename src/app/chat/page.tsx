import { AppShell } from "@/components/shell/AppShell"
import ChatPage from "@/components/pages/ChatPage"

export default function Chat() {
  return (
    <AppShell activeTab="chat">
      <ChatPage />
    </AppShell>
  )
}
