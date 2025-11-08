"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { analyzeRecipe } from "@/lib/api";

export default function AnalyzePage() {
  const [recipe, setRecipe] = useState("");
  const [urgency, setUrgency] = useState("tonight");
  const router = useRouter();

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const res = await analyzeRecipe({
      user_id: "72cf83a7-8d4c-4c99-874a-d88d16f0d0a0",
      recipe_text: recipe,
      urgency,
    });
    router.push(`/dashboard?recipe=${res.recipe_id}`);
  }

  return (
    <form onSubmit={handleSubmit} className="p-6 flex flex-col gap-4">
      <textarea
        placeholder="Paste your recipe..."
        value={recipe}
        onChange={(event) => setRecipe(event.target.value)}
        className="border p-3 rounded"
        rows={6}
      />
      <select
        value={urgency}
        onChange={(event) => setUrgency(event.target.value)}
        className="border p-2 rounded"
      >
        <option value="tonight">Tonight</option>
        <option value="soon">Soon</option>
        <option value="later">Later</option>
      </select>
      <button type="submit" className="bg-green-500 text-white p-2 rounded">
        Analyze Recipe
      </button>
    </form>
  );
}
