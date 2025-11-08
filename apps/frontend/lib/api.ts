export async function analyzeRecipe(payload: Record<string, unknown>) {
  const res = await fetch(`${process.env.BACKEND_URL}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    throw new Error(`Analyze failed: ${res.status}`);
  }

  return res.json();
}

export async function simulateRecipe(recipeId: string) {
  const res = await fetch(`${process.env.BACKEND_URL}/simulate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ recipe_id: recipeId }),
  });

  if (!res.ok) {
    throw new Error(`Simulate failed: ${res.status}`);
  }

  return res.json();
}
