"use client"

import { useState, useRef, useEffect } from "react"
import { useBananakart } from "@/context/BananakartContext"

export default function ChatPage() {
  const { chatMessages, addChatMessage } = useBananakart()
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [chatMessages])

  const handleSendMessage = async () => {
    if (!input.trim()) return

    addChatMessage(input, "user")
    setInput("")
    setLoading(true)

    setTimeout(() => {
      const responses = [
        "I found some fresh tomatoes perfect for your salad! Would you like me to add them to your cart?",
        "Based on your recent orders, I recommend these seasonal herbs. They're in stock at nearby stores.",
        "Your weekly box is ready! I've pre-selected items based on your preferences.",
      ]
      const randomResponse = responses[Math.floor(Math.random() * responses.length)]
      addChatMessage(randomResponse, "assistant")
      setLoading(false)
    }, 1000)
  }

  const quickSuggestions = [
    "Show me organic vegetables",
    "What's on sale today?",
    "Suggest a meal plan",
    "Track my order",
  ]

  return (
    <div className="h-screen flex flex-col">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
        {chatMessages.length === 0 ? (
          <div className="h-full flex flex-col justify-center items-center text-center">
            <div className="text-4xl mb-4">💬</div>
            <h3 className="text-lg font-semibold mb-2">Welcome to Bananakart Chat</h3>
            <p className="text-muted-foreground text-sm max-w-xs">
              Ask me anything about our products, your orders, or get personalized recommendations.
            </p>
            <div className="mt-6 w-full space-y-2">
              {quickSuggestions.map((suggestion, i) => (
                <button
                  key={i}
                  onClick={() => {
                    setInput(suggestion)
                  }}
                  className="w-full btn-secondary text-sm text-left"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <>
            {chatMessages.map((message) => (
              <div key={message.id} className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}>
                <div
                  className={`max-w-xs p-3 rounded-lg text-sm ${
                    message.role === "user" ? "bg-primary text-primary-foreground" : "card-glass"
                  }`}
                >
                  {message.content}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="card-glass p-3 rounded-lg">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-accent rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-accent rounded-full animate-bounce delay-100"></div>
                    <div className="w-2 h-2 bg-accent rounded-full animate-bounce delay-200"></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input Area */}
      <div className="border-t border-border bg-card p-4 safe-area-inset-bottom">
        <div className="max-w-2xl mx-auto flex gap-2">
          <input
            type="text"
            placeholder="Ask about products, orders, or recommendations..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
            disabled={loading}
            className="flex-1 bg-background border border-border rounded-lg px-4 py-2 text-sm text-foreground placeholder-muted-foreground focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/30 transition disabled:opacity-50"
          />
          <button
            onClick={handleSendMessage}
            disabled={loading || !input.trim()}
            className="btn-primary text-sm py-2 px-4 disabled:opacity-50"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  )
}
