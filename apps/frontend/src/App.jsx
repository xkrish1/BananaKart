import React, { useState } from "react";

export default function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  async function sendRecipe() {
    setLoading(true);
    const recipe = {
      user_id: "test-user-001",
      recipe_text: "Grilled chicken with rice and steamed broccoli for dinner tonight",
      urgency: "tonight"
    };

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(recipe)
      });
      const data = await response.json();
      setResult(data);
    } catch (err) {
      console.error("Request failed", err);
      setResult({ error: "Connection failed" });
    } finally {
      setLoading(false);
    }
  }

  return (
    <main style={{ textAlign: "center", marginTop: "4rem" }}>
      <h1>BananaKart 🍌</h1>
      <p>Send a recipe to the backend and view the response.</p>
      <button onClick={sendRecipe} disabled={loading}>
        {loading ? "Analyzing..." : "Analyze Recipe"}
      </button>
      {result && (
        <pre
          style={{
            marginTop: "2rem",
            background: "#f4f4f4",
            padding: "1rem",
            borderRadius: "8px",
            textAlign: "left"
          }}
        >
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
    </main>
  );
}
