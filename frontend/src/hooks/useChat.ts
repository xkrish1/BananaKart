"use client"

import { useState } from "react"

export function useChat() {
  const [messages, setMessages] = useState<Array<{ role: "user" | "assistant"; content: string }>>([])
  const [loading, setLoading] = useState(false)

  const sendMessage = async (message: string) => {
    // Would connect to /api/chat endpoint
    setMessages((prev) => [...prev, { role: "user", content: message }])
    setLoading(true)

    // Simulate response
    setTimeout(() => {
      setMessages((prev) => [...prev, { role: "assistant", content: "Chat response..." }])
      setLoading(false)
    }, 1000)
  }

  return { messages, loading, sendMessage }
}
