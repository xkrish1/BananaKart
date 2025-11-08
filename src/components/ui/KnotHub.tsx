"use client"

import { useState } from "react"

export default function KnotHub() {
  const [saved, setSaved] = useState(3)

  const suggestions = [
    { id: 1, text: "Reorder your weekly vegetables", icon: "🥬" },
    { id: 2, text: "Try new seasonal items", icon: "🍊" },
    { id: 3, text: "Save with our family bundle", icon: "👨‍👩‍👧‍👦" },
  ]

  return (
    <div className="space-y-2">
      {suggestions.map((suggestion) => (
        <div key={suggestion.id} className="card-glass p-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <span className="text-2xl">{suggestion.icon}</span>
            <p className="text-sm">{suggestion.text}</p>
          </div>
          <button className="btn-secondary text-xs py-1 px-2">Explore</button>
        </div>
      ))}
      <p className="text-xs text-muted text-center mt-4">{saved} smart suggestions saved for you</p>
    </div>
  )
}
