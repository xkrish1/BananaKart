"use client";

import { useState } from "react";

const CookPage = () => {
  const [text, setText] = useState("");
  const [servings, setServings] = useState<number>(1);
  const [zipcode, setZipcode] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setNotice(null);
    setResult(null);
    try {
      const payload: Record<string, unknown> = { text };
      if (servings && servings > 0) {
        payload.servings = servings;
      }
      if (zipcode.trim()) {
        payload.zipcode = zipcode.trim();
      }
      const res = await fetch("/llm_recipe", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        const detail = await res.text();
        throw new Error(detail || "Request failed");
      }
      const data = await res.json();
      if (data.response_type === "need_zip") {
        setNotice(data.message ?? "Please provide your ZIP code.");
        return;
      }
      setResult(data);
      setNotice(data.message ?? null);
    } catch (err: any) {
      setError(err.message ?? "Unexpected error");
    } finally {
      setLoading(false);
    }
  };

  const handleSource = () => {
    if (!result?.recipe?.ingredients) return;
    window.dispatchEvent(
      new CustomEvent("bananakart:source", { detail: result.recipe.ingredients })
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
        <label className="flex w-full max-w-[200px] flex-col gap-2">
          <span className="text-sm font-medium">ZIP Code</span>
          <input
            type="text"
            className="rounded border border-gray-300 p-2"
            value={zipcode}
            onChange={(e) => setZipcode(e.target.value)}
            placeholder="02108"
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

      {notice && !result && (
        <div className="rounded border border-blue-200 bg-blue-50 p-3 text-sm text-blue-700">
          {notice}
        </div>
      )}

      {result && (
        <div className="space-y-4">
          <div className="flex flex-col gap-2">
            <span className="rounded bg-blue-100 px-3 py-1 text-sm font-medium text-blue-700">
              {notice ?? "Recipe plan ready"}
            </span>
            <span className="text-sm text-gray-600">
              Servings: {result.recipe?.servings ?? servings}
            </span>
          </div>

          {result.recipe?.title && (
            <h2 className="text-2xl font-semibold">{result.recipe.title}</h2>
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
                  {result.recipe?.ingredients?.map((item: any, idx: number) => (
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

          {result.recipe?.steps?.length > 0 && (
            <div>
              <h3 className="text-lg font-medium">Steps</h3>
              <ol className="list-decimal space-y-2 pl-5 text-sm text-gray-700">
                {result.recipe.steps.map((step: string, idx: number) => (
                  <li key={idx}>{step}</li>
                ))}
              </ol>
            </div>
          )}

          {result.sourcing?.farmers_markets?.length ? (
            <div>
              <h3 className="text-lg font-medium">Farmers Markets</h3>
              <div className="space-y-2 text-sm text-gray-700">
                {result.sourcing.farmers_markets.map(
                  (entry: any, idx: number) => (
                    <div key={idx} className="rounded border border-emerald-200 p-3">
                      <div className="font-semibold text-emerald-700">
                        {entry.market?.name}
                      </div>
                      <div className="text-gray-600">
                        {entry.market?.address} • {entry.market?.hours}
                      </div>
                      <ul className="mt-2 list-disc pl-5">
                        {entry.items?.map((item: any, itemIdx: number) => (
                          <li key={itemIdx}>
                            {item?.name}{" "}
                            {item?.quantity != null
                              ? `• ${item.quantity}`
                              : ""}{" "}
                            {item?.unit ?? ""}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )
                )}
              </div>
            </div>
          ) : null}

          {result.sourcing?.big_box?.length ? (
            <div>
              <h3 className="text-lg font-medium">Big-Box Options</h3>
              <div className="space-y-2 text-sm text-gray-700">
                {result.sourcing.big_box.map((entry: any, idx: number) => (
                  <div key={idx} className="rounded border border-gray-200 p-3">
                    <div className="font-semibold text-gray-800">
                      {entry.store?.name}
                    </div>
                    <div className="text-gray-600">{entry.store?.address}</div>
                    <ul className="mt-2 list-disc pl-5">
                      {entry.items?.map((item: any, itemIdx: number) => (
                        <li key={itemIdx}>
                          {item?.name}{" "}
                          {item?.quantity != null ? `• ${item.quantity}` : ""}{" "}
                          {item?.unit ?? ""}
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </div>
          ) : null}

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
