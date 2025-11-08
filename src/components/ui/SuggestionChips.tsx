"use client"

interface SuggestionChipsProps {
  suggestions: string[]
  onSelect: (suggestion: string) => void
}

export default function SuggestionChips({ suggestions, onSelect }: SuggestionChipsProps) {
  return (
    <div className="flex flex-wrap gap-2">
      {suggestions.map((suggestion, i) => (
        <button
          key={i}
          onClick={() => onSelect(suggestion)}
          className="px-3 py-1.5 rounded-full bg-accent/20 border border-accent text-accent text-xs hover:bg-accent/30 transition"
        >
          {suggestion}
        </button>
      ))}
    </div>
  )
}
