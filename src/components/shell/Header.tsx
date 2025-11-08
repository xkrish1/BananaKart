"use client"
import Link from "next/link"
import { useTheme } from "@/context/ThemeContext"
import { useBananakart } from "@/context/BananakartContext"

const tabs = [
  { name: "Home", id: "home", icon: "🏠" },
  { name: "Explore", id: "explore", icon: "🔍" },
  { name: "Map", id: "map", icon: "🗺️" },
  { name: "Dashboard", id: "dashboard", icon: "📊" },
  { name: "Chat", id: "chat", icon: "💬" },
]

export function Header({ activeTab = "home" }: { activeTab?: string }) {
  const { isDark, toggleTheme } = useTheme()
  const { cart } = useBananakart()
  const cartCount = cart.reduce((sum, item) => sum + item.quantity, 0)

  return (
    <header className="sticky top-0 z-50 border-b border-border bg-card shadow-sm">
      <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
        {/* Logo on left */}
        <Link href="/" className="flex items-center gap-2">
          <span className="text-2xl">🍌</span>
          <h1 className="text-xl font-bold text-primary hidden sm:inline">Bananakart</h1>
        </Link>

        {/* Navigation tabs in center */}
        <nav className="hidden md:flex items-center gap-1">
          {tabs.map((tab) => (
            <Link
              key={tab.id}
              href={`/${tab.id === "home" ? "" : tab.id}`}
              className={`px-4 py-2 rounded-lg transition flex items-center gap-2 text-sm ${
                activeTab === tab.id ? "bg-primary text-primary-foreground" : "text-foreground hover:bg-muted"
              }`}
              title={tab.name}
            >
              <span>{tab.icon}</span>
              <span>{tab.name}</span>
            </Link>
          ))}
        </nav>

        {/* Cart and theme toggle on right */}
        <div className="flex items-center gap-3">
          {/* Cart button */}
          <Link
            href="/orders"
            className={`relative p-2 rounded-lg transition ${
              activeTab === "orders" ? "bg-primary text-primary-foreground" : "text-foreground hover:bg-muted"
            }`}
            title="Cart"
          >
            <span className="text-xl">🛒</span>
            {cartCount > 0 && (
              <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center">
                {cartCount}
              </span>
            )}
          </Link>

          {/* Theme toggle */}
          <button
            onClick={toggleTheme}
            className="p-2 rounded-lg hover:bg-muted transition-colors"
            aria-label="Toggle theme"
            title={isDark ? "Light mode" : "Dark mode"}
          >
            {isDark ? "☀️" : "🌙"}
          </button>

          {/* Mobile menu - show nav tabs for mobile */}
          <div className="md:hidden flex items-center gap-1">
            {tabs.map((tab) => (
              <Link
                key={tab.id}
                href={`/${tab.id === "home" ? "" : tab.id}`}
                className={`p-2 rounded-lg transition text-lg ${
                  activeTab === tab.id ? "bg-primary text-primary-foreground" : "text-foreground hover:bg-muted"
                }`}
                title={tab.name}
              >
                {tab.icon}
              </Link>
            ))}
          </div>
        </div>
      </div>
    </header>
  )
}
