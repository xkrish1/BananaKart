"use client";

import { useState } from "react";

const CookPage = () => {
  const [text, setText] = useState("");
  const [servings, setServings] = useState<number>(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const payload: Record<string, unknown> = { text };
      if (servings && servings > 0) {
        payload.servings = servings;
      }
      const res = await fetch("/analyze_or_generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        const detail = await res.text();
        throw new Error(detail || "Request failed");
      }
      const data = await res.json();
      setResult(data);
    } catch (err: any) {
      setError(err.message ?? "Unexpected error");
    } finally {
      setLoading(false);
    }
  };

  const handleSource = () => {
    if (!result?.ingredients) return;
    window.dispatchEvent(
      new CustomEvent("bananakart:source", { detail: result.ingredients })
    );
  };

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-6 px-4 py-8">
      <h1 className="text-3xl font-semibold">Cook with BananaKart</h1>
      <form onSubmit={submit} className="flex flex-col gap-4">
        <label className="flex flex-col gap-2">
          <span className="text-sm font-medium">
            What do you want to make or paste a recipe?
          </span>
          <textarea
            className="min-h-[160px] rounded border border-gray-300 p-3"
            placeholder="e.g. how to make spicy salsa"
            value={text}
            onChange={(e) => setText(e.target.value)}
            required
          />
        </label>
        <label className="flex w-full max-w-[160px] flex-col gap-2">
          <span className="text-sm font-medium">Servings</span>
          <input
            type="number"
            min={1}
            className="rounded border border-gray-300 p-2"
            value={servings}
            onChange={(e) => setServings(Number(e.target.value) || 1)}
          />
        </label>
        <button
          type="submit"
          className="inline-flex items-center justify-center rounded bg-emerald-600 px-4 py-2 font-medium text-white hover:bg-emerald-700"
          disabled={loading}
        >
          {loading ? "Working..." : "Analyze or Generate"}
        </button>
      </form>

      {error && (
        <div className="rounded border border-red-300 bg-red-50 p-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {result && (
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <span className="rounded-full bg-blue-100 px-3 py-1 text-sm font-medium text-blue-700">
              Mode: {result.mode === "parse" ? "Parse" : "Generate"}
            </span>
            {result.servings && (
              <span className="text-sm text-gray-600">
                Servings: {result.servings}{" "}
                {result.servings_assumed ? "(assumed)" : ""}
              </span>
            )}
          </div>

          {result.title && (
            <h2 className="text-2xl font-semibold">{result.title}</h2>
          )}

          <div>
            <h3 className="text-lg font-medium">Ingredients</h3>
            <div className="overflow-x-auto">
              <table className="mt-2 w-full border-collapse text-sm">
                <thead>
                  <tr className="bg-gray-100 text-left">
                    <th className="border border-gray-200 px-3 py-2">Name</th>
                    <th className="border border-gray-200 px-3 py-2">Quantity</th>
                    <th className="border border-gray-200 px-3 py-2">Unit</th>
                  </tr>
                </thead>
                <tbody>
                  {result.ingredients?.map((item: any, idx: number) => (
                    <tr key={idx}>
                      <td className="border border-gray-200 px-3 py-2">
                        {item?.name ?? ""}
                      </td>
                      <td className="border border-gray-200 px-3 py-2">
                        {item?.quantity ?? ""}
                      </td>
                      <td className="border border-gray-200 px-3 py-2">
                        {item?.unit ?? ""}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {result.mode === "generate" && result.steps?.length > 0 && (
            <div>
              <h3 className="text-lg font-medium">Steps</h3>
              <ol className="list-decimal space-y-2 pl-5 text-sm text-gray-700">
                {result.steps.map((step: string, idx: number) => (
                  <li key={idx}>{step}</li>
                ))}
              </ol>
            </div>
          )}

          <button
            type="button"
            onClick={handleSource}
            className="rounded border border-emerald-600 px-4 py-2 text-sm font-medium text-emerald-700 hover:bg-emerald-50"
          >
            Source locally
          </button>
        </div>
      )}
    </div>
  );
};

export default CookPage;
