export function useSlots() {
  const slots = [
    { id: "1", time: "10:00 - 12:00", date: "Tomorrow", available: true },
    { id: "2", time: "14:00 - 16:00", date: "Tomorrow", available: true },
    { id: "3", time: "18:00 - 20:00", date: "Tomorrow", available: false },
  ]

  return { slots }
}
