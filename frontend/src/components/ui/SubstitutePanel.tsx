"use client"

interface Product {
  id: string
  name: string
  price: number
  category?: string
  image?: string
}

interface SubstitutePanelProps {
  product: Product
  substitutes: Product[]
  onSelect: (product: Product) => void
}

export default function SubstitutePanel({ substitutes, onSelect }: SubstitutePanelProps) {
  return (
    <div className="card-glass p-4">
      <h4 className="font-semibold mb-3">Similar Items</h4>
      <div className="space-y-2">
        {substitutes.map((sub) => (
          <button
            key={sub.id}
            onClick={() => onSelect(sub)}
            className="w-full text-left p-3 rounded-lg bg-slate-800 hover:bg-slate-700 transition text-sm"
          >
            <div className="flex justify-between items-center">
              <span>{sub.name}</span>
              <span className="text-primary font-bold">${sub.price}</span>
            </div>
            <p className="text-xs text-muted mt-1">{sub.category}</p>
          </button>
        ))}
      </div>
    </div>
  )
}
