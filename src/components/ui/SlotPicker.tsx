"use client"

import { useState } from "react"

interface TimeSlot {
  id: string
  time: string
  date: string
  available: boolean
}

const mockSlots: TimeSlot[] = [
  { id: "1", time: "10:00 - 12:00", date: "Tomorrow", available: true },
  { id: "2", time: "14:00 - 16:00", date: "Tomorrow", available: true },
  { id: "3", time: "18:00 - 20:00", date: "Tomorrow", available: false },
  { id: "4", time: "10:00 - 12:00", date: "Day After", available: true },
  { id: "5", time: "14:00 - 16:00", date: "Day After", available: true },
]

export default function SlotPicker() {
  const [selected, setSelected] = useState<string | null>(null)

  return (
    <div className="card-glass p-4">
      <h3 className="font-semibold mb-4">Choose Delivery Slot</h3>
      <div className="grid grid-cols-1 gap-2 mb-4">
        {mockSlots.map((slot) => (
          <button
            key={slot.id}
            onClick={() => slot.available && setSelected(slot.id)}
            disabled={!slot.available}
            className={`p-3 rounded-lg text-sm transition ${
              selected === slot.id
                ? "bg-primary text-primary-foreground"
                : slot.available
                  ? "bg-slate-800 hover:border-accent border border-slate-700"
                  : "bg-slate-900 text-muted opacity-50 cursor-not-allowed"
            }`}
          >
            <div className="flex justify-between items-center">
              <span className="font-medium">{slot.time}</span>
              <span className="text-xs opacity-75">{slot.date}</span>
            </div>
          </button>
        ))}
      </div>
      <button disabled={!selected} className="btn-primary w-full disabled:opacity-50">
        Confirm Delivery
      </button>
    </div>
  )
}
