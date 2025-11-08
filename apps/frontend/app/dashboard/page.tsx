"use client";
import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { simulateRecipe } from "@/lib/api";
import { supabase } from "@/lib/supabaseClient";

interface EcoResult {
  eco_score: number;
  co2_saved_kg: number;
  variance_cost: number;
  best_sources: string[];
}

export default function DashboardPage() {
  const searchParams = useSearchParams();
  const recipeId = searchParams.get("recipe");
  const [data, setData] = useState<EcoResult | null>(null);

  useEffect(() => {
    if (!recipeId) {
      return;
    }

    simulateRecipe(recipeId).then(setData).catch(console.error);

    const channel = supabase
      .channel("eco_results")
      .on(
        "postgres_changes",
        {
          event: "*",
          schema: "public",
          table: "eco_results",
        },
        (payload) => {
          const newRow = payload.new as EcoResult & { recipe_id: string };
          if (newRow.recipe_id === recipeId) {
            setData({
              eco_score: newRow.eco_score,
              co2_saved_kg: newRow.co2_saved_kg,
              variance_cost: newRow.variance_cost,
              best_sources: newRow.best_sources,
            });
          }
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, [recipeId]);

  if (!recipeId) {
    return <p className="p-6">Recipe not specified.</p>;
  }

  if (!data) {
    return <p className="p-6">Loading...</p>;
  }

  return (
    <div className="p-6 grid gap-4">
      <div className="text-xl font-semibold">Eco Score: {data.eco_score.toFixed(2)}</div>
      <div>CO₂ Saved (kg): {data.co2_saved_kg.toFixed(2)}</div>
      <div>Cost Variance: {data.variance_cost.toFixed(2)}</div>
      <div>Best Sources: {data.best_sources.join(", ")}</div>
    </div>
  );
}
