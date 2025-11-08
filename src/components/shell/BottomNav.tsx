"use client"
import Link from "next/link"

const tabs = [
  { name: "Home", id: "home", icon: "🏠" },
  { name: "Explore", id: "explore", icon: "🔍" },
  { name: "Map", id: "map", icon: "🗺️" },
  { name: "Dashboard", id: "dashboard", icon: "📊" },
  { name: "Chat", id: "chat", icon: "💬" },
]

export function BottomNav({ activeTab = "home" }: { activeTab?: string }) {
  return (
    <nav className="fixed bottom-0 left-0 right-0 border-t border-border bg-card safe-area-inset-bottom flex justify-around items-center h-16 md:relative md:border-r md:border-t-0 md:w-16 md:h-screen md:flex-col md:justify-start md:pt-4">
      {tabs.map((tab) => (
        <Link
          key={tab.id}
          href={`/${tab.id === "home" ? "" : tab.id}`}
          className={`flex flex-col items-center justify-center w-16 h-16 rounded-lg transition ${
            activeTab === tab.id ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:bg-muted"
          }`}
          title={tab.name}
        >
          <span className="text-2xl">{tab.icon}</span>
          <span className="text-xs mt-1 hidden md:block">{tab.name}</span>
        </Link>
      ))}
    </nav>
  )
}
