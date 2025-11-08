"use client"

interface FilterChipsProps {
  options: string[]
  selected: string
  onSelect: (option: string) => void
  label?: string
}

export default function FilterChips({ options, selected, onSelect, label }: FilterChipsProps) {
  return (
    <div>
      {label && <p className="text-sm text-muted mb-2">{label}</p>}
      <div className="flex flex-wrap gap-2">
        {options.map((option) => (
          <button
            key={option}
            onClick={() => onSelect(option)}
            className={`px-3 py-1.5 rounded-lg text-sm transition ${
              selected === option
                ? "bg-primary text-primary-foreground"
                : "bg-slate-800 border border-slate-700 text-muted hover:border-accent"
            }`}
          >
            {option}
          </button>
        ))}
      </div>
    </div>
  )
}
