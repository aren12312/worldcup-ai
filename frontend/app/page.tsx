"use client";

import { FormEvent, useState } from "react";
import {
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";

type Prediction = {
  match: string;
  probabilities: {
    team1_win: number;
    draw: number;
    team2_win: number;
  };
  expected_goals: Record<string, number>;
  analysis: string[];
  upset_risk: string;
  recommendation: string;
  data_sources: Record<string, string>;
};

const COLORS = ["#22c55e", "#94a3b8", "#3b82f6"];

export default function Home() {
  const [team1, setTeam1] = useState("Brazil");
  const [team2, setTeam2] = useState("France");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<Prediction | null>(null);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const params = new URLSearchParams({ team1, team2 });
      const response = await fetch(`${API_URL}/predict?${params}`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Prediction failed");
      }

      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  const chartData = result
    ? (() => {
        const [home, away] = result.match.split(" vs ");
        return [
          { name: home, value: result.probabilities.team1_win },
          { name: "Draw", value: result.probabilities.draw },
          { name: away, value: result.probabilities.team2_win },
        ];
      })()
    : [];

  return (
    <main className="min-h-screen bg-gradient-to-b from-pitch-950 via-pitch-900 to-pitch-950">
      <div className="mx-auto max-w-5xl px-4 py-12">
        <header className="mb-10 text-center">
          <p className="mb-2 text-sm uppercase tracking-[0.3em] text-gold">
            World Cup 2026
          </p>
          <h1 className="text-4xl font-bold md:text-5xl">AI Match Analyst</h1>
          <p className="mx-auto mt-4 max-w-2xl text-white/70">
            Data-driven predictions with Poisson simulation and research-backed
            analysis. Enter any two national teams.
          </p>
        </header>

        <form
          onSubmit={handleSubmit}
          className="mx-auto mb-10 max-w-3xl rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur"
        >
          <div className="grid gap-4 md:grid-cols-[1fr_auto_1fr_auto] md:items-end">
            <label className="block">
              <span className="mb-2 block text-sm text-white/60">Team 1</span>
              <input
                value={team1}
                onChange={(e) => setTeam1(e.target.value)}
                className="w-full rounded-xl border border-white/10 bg-pitch-950 px-4 py-3 outline-none ring-gold focus:ring-2"
                placeholder="Brazil"
              />
            </label>

            <div className="hidden pb-3 text-center text-gold md:block">VS</div>

            <label className="block">
              <span className="mb-2 block text-sm text-white/60">Team 2</span>
              <input
                value={team2}
                onChange={(e) => setTeam2(e.target.value)}
                className="w-full rounded-xl border border-white/10 bg-pitch-950 px-4 py-3 outline-none ring-gold focus:ring-2"
                placeholder="France"
              />
            </label>

            <button
              type="submit"
              disabled={loading}
              className="rounded-xl bg-gold px-6 py-3 font-semibold text-pitch-950 transition hover:brightness-110 disabled:opacity-60"
            >
              {loading ? "Analyzing..." : "Analyze Match"}
            </button>
          </div>
        </form>

        {error && (
          <div className="mx-auto mb-8 max-w-3xl rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-red-200">
            {error}
          </div>
        )}

        {result && (
          <section className="mx-auto grid max-w-5xl gap-6 md:grid-cols-2">
            <div className="rounded-2xl border border-white/10 bg-white/5 p-6">
              <h2 className="mb-4 text-2xl font-semibold">{result.match}</h2>

              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={chartData}
                      dataKey="value"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      innerRadius={55}
                      outerRadius={90}
                      paddingAngle={3}
                    >
                      {chartData.map((_, index) => (
                        <Cell key={index} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value: number) => `${value}%`} />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              <div className="mt-4 grid grid-cols-3 gap-2 text-center text-sm">
                {chartData.map((item, index) => (
                  <div key={item.name} className="rounded-lg bg-black/20 p-3">
                    <div
                      className="mx-auto mb-2 h-2 w-8 rounded-full"
                      style={{ backgroundColor: COLORS[index] }}
                    />
                    <p className="text-white/60">{item.name}</p>
                    <p className="text-lg font-bold">{item.value}%</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="space-y-6">
              <div className="rounded-2xl border border-white/10 bg-white/5 p-6">
                <h3 className="mb-3 text-lg font-semibold">Expected Goals</h3>
                <div className="space-y-2">
                  {Object.entries(result.expected_goals).map(([team, xg]) => (
                    <div
                      key={team}
                      className="flex items-center justify-between rounded-lg bg-black/20 px-4 py-2"
                    >
                      <span>{team}</span>
                      <span className="font-bold text-gold">{xg}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="rounded-2xl border border-white/10 bg-white/5 p-6">
                <h3 className="mb-3 text-lg font-semibold">Analysis</h3>
                <ul className="space-y-3 text-white/80">
                  {result.analysis.map((point, index) => (
                    <li key={index} className="flex gap-2">
                      <span className="text-gold">•</span>
                      <span>{point}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="rounded-2xl border border-gold/30 bg-gold/10 p-6">
                <h3 className="mb-2 text-lg font-semibold text-gold">
                  Recommendation
                </h3>
                <p className="text-white/90">{result.recommendation}</p>
                <p className="mt-3 text-sm text-white/60">
                  Upset risk:{" "}
                  <span className="font-semibold capitalize text-white">
                    {result.upset_risk}
                  </span>
                </p>
              </div>
            </div>
          </section>
        )}
      </div>
    </main>
  );
}
