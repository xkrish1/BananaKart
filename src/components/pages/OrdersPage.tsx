"use client"

import { useState } from "react"
import { useBananakart } from "@/context/BananakartContext"
import SlotPicker from "@/components/ui/SlotPicker"
import ImpactWidget from "@/components/ui/ImpactWidget"
import SubstitutePanel from "@/components/ui/SubstitutePanel"

export default function OrdersPage() {
  const { cart, orders, addOrder } = useBananakart()
  const [showSlotPicker, setShowSlotPicker] = useState(false)

  const handleCheckout = () => {
    if (cart.length > 0) {
      const newOrder = {
        id: `ORD-${Date.now()}`,
        items: cart,
        status: "confirmed" as const,
        total: cart.reduce((sum, item) => sum + item.price * item.quantity, 0),
        createdAt: new Date().toLocaleDateString(),
      }
      addOrder(newOrder)
      setShowSlotPicker(true)
    }
  }

  const cartTotal = cart.reduce((sum, item) => sum + item.price * item.quantity, 0)
  const cartImpact = (cart.length * 0.35).toFixed(1) // kg CO2 saved

  if (showSlotPicker) {
    return (
      <div className="px-4 py-6 max-w-2xl mx-auto space-y-6">
        <div className="text-center">
          <div className="text-4xl mb-4">✅</div>
          <h2 className="text-2xl font-bold mb-2">Order Confirmed!</h2>
          <p className="text-muted">Select your delivery slot.</p>
        </div>
        <SlotPicker />
      </div>
    )
  }

  return (
    <div className="px-4 py-6 max-w-2xl mx-auto space-y-6">
      {/* Your Cart */}
      <section>
        <h2 className="text-2xl font-bold mb-4">Your Cart</h2>
        {cart.length > 0 ? (
          <div className="space-y-2">
            {cart.map((item) => (
              <div key={item.id} className="card-glass p-4 flex justify-between items-center">
                <div>
                  <p className="font-semibold">{item.name}</p>
                  <p className="text-xs text-muted">Qty: {item.quantity}</p>
                </div>
                <p className="text-primary font-bold">${(item.price * item.quantity).toFixed(2)}</p>
              </div>
            ))}
          </div>
        ) : (
          <div className="card-glass p-8 text-center text-muted">
            <p>Your cart is empty. Start shopping!</p>
          </div>
        )}
      </section>

      {/* Impact Widget */}
      {cart.length > 0 && <ImpactWidget carbonSaved={cartImpact} itemsCount={cart.length} />}

      {/* Substitute Options */}
      {cart.length > 0 && (
        <section>
          <h3 className="text-lg font-semibold mb-4">Similar Items</h3>
          <SubstitutePanel
            product={cart[0]}
            substitutes={[
              { id: "s1", name: "Cherry Tomatoes", category: "Vegetables", price: 5.99 },
              { id: "s2", name: "Heirloom Mix", category: "Vegetables", price: 6.99 },
            ]}
            onSelect={(item) => console.log("Selected:", item)}
          />
        </section>
      )}

      {/* Order Summary */}
      {cart.length > 0 && (
        <div className="card-glass p-4 border-t border-slate-700">
          <div className="space-y-2 mb-4">
            <div className="flex justify-between text-sm">
              <span>Subtotal</span>
              <span>${cartTotal.toFixed(2)}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span>Delivery</span>
              <span className="text-green-400">Free</span>
            </div>
            <div className="border-t border-slate-700 pt-2 flex justify-between font-bold">
              <span>Total</span>
              <span className="text-primary">${cartTotal.toFixed(2)}</span>
            </div>
          </div>
          <button onClick={handleCheckout} className="btn-primary w-full">
            Proceed to Checkout
          </button>
        </div>
      )}

      {/* Recent Orders */}
      {orders.length > 0 && (
        <section>
          <h3 className="text-lg font-semibold mb-4">Order History</h3>
          <div className="space-y-2">
            {orders.slice(0, 3).map((order) => (
              <div key={order.id} className="card-glass p-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-semibold">{order.id}</span>
                  <span className="text-xs bg-green-900 text-green-200 px-2 py-1 rounded">{order.status}</span>
                </div>
                <p className="text-xs text-muted mt-1">
                  ${order.total} • {order.createdAt}
                </p>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  )
}
