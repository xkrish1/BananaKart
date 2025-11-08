"use client"

import type React from "react"

import { createContext, useContext, useState } from "react"

export interface CartItem {
  id: string
  name: string
  price: number
  quantity: number
  image?: string
}

export interface Order {
  id: string
  items: CartItem[]
  status: "pending" | "confirmed" | "preparing" | "ready" | "delivered"
  total: number
  createdAt: string
}

interface BananakartContextType {
  cart: CartItem[]
  addToCart: (item: CartItem) => void
  removeFromCart: (id: string) => void
  updateCartQty: (id: string, qty: number) => void
  clearCart: () => void
  orders: Order[]
  addOrder: (order: Order) => void
  chatMessages: Array<{ id: string; role: "user" | "assistant"; content: string }>
  addChatMessage: (message: string, role: "user" | "assistant") => void
}

const BananakartContext = createContext<BananakartContextType | undefined>(undefined)

export function BananakartProvider({ children }: { children: React.ReactNode }) {
  const [cart, setCart] = useState<CartItem[]>([])
  const [orders, setOrders] = useState<Order[]>([])
  const [chatMessages, setChatMessages] = useState<Array<{ id: string; role: "user" | "assistant"; content: string }>>(
    [],
  )

  const addToCart = (item: CartItem) => {
    setCart((prev) => {
      const existing = prev.find((i) => i.id === item.id)
      if (existing) {
        return prev.map((i) => (i.id === item.id ? { ...i, quantity: i.quantity + item.quantity } : i))
      }
      return [...prev, item]
    })
  }

  const removeFromCart = (id: string) => {
    setCart((prev) => prev.filter((i) => i.id !== id))
  }

  const updateCartQty = (id: string, qty: number) => {
    setCart((prev) => prev.map((i) => (i.id === id ? { ...i, quantity: qty } : i)))
  }

  const clearCart = () => setCart([])

  const addOrder = (order: Order) => {
    setOrders((prev) => [order, ...prev])
  }

  const addChatMessage = (content: string, role: "user" | "assistant") => {
    setChatMessages((prev) => [...prev, { id: crypto.getRandomValues(new Uint8Array(4)).join(""), role, content }])
  }

  return (
    <BananakartContext.Provider
      value={{
        cart,
        addToCart,
        removeFromCart,
        updateCartQty,
        clearCart,
        orders,
        addOrder,
        chatMessages,
        addChatMessage,
      }}
    >
      {children}
    </BananakartContext.Provider>
  )
}

export function useBananakart() {
  const context = useContext(BananakartContext)
  if (!context) throw new Error("useBananakart must be used within BananakartProvider")
  return context
}
