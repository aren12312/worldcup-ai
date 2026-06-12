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
  lang: string;
  match: string;
  probabilities: {
    team1_win: number;
    draw: number;
    team2_win: number;
  };
  labels: {
    team1: string;
    team2: string;
    draw: string;
  };
  expected_goals: Record<string, number>;
  analysis: string[];
  summary: string;
  detailed: string;
  key_factors: string[];
  recent_form: Record<string, string[]>;
  head_to_head: string[];
  h2h_summary: string;
  upset_risk: string;
  recommendation: string;
  data_quality: string;
  has_live_data: boolean;
  data_sources: Record<string, string>;
  market_odds?: { odds?: Record<string, number>; event?: string } | null;
  weather?: { city?: string; description?: string; temp_c?: number; impact_he?: string } | null;
};

const COLORS = ["#22c55e", "#94a3b8", "#3b82f6"];

const POPULAR_MATCHES = [
  ["ברזיל", "צרפת"],
  ["ארגנטינה", "אנגליה"],
  ["ספרד", "גרמניה"],
  ["פורטוגל", "הולנד"],
];

export default function Home() {
  const [team1, setTeam1] = useState("ברזיל");
  const [team2, setTeam2] = useState("צרפת");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<Prediction | null>(null);

  async function analyze(t1: string, t2: string) {
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const params = new URLSearchParams({ team1: t1, team2: t2, lang: "he" });
      const response = await fetch(`${API_URL}/predict?${params}`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "הניתוח נכשל");
      }

      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "משהו השתבש");
    } finally {
      setLoading(false);
    }
  }

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    analyze(team1, team2);
  }

  const chartData = result
    ? [
        { name: result.labels.team1, value: result.probabilities.team1_win },
        { name: result.labels.draw, value: result.probabilities.draw },
        { name: result.labels.team2, value: result.probabilities.team2_win },
      ]
    : [];

  return (
    <main
      dir="rtl"
      className="min-h-screen bg-gradient-to-b from-pitch-950 via-pitch-900 to-black"
    >
      <div className="mx-auto max-w-6xl px-4 py-10">
        <header className="mb-10 text-center">
          <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-gold/30 bg-gold/10 px-4 py-1 text-sm text-gold">
            <span>🏆</span>
            <span>מונדיאל 2026 — ניתוח מבוסס משחקים אמיתיים</span>
          </div>
          <h1 className="text-4xl font-bold md:text-5xl">אנליסט AI למשחקי כדורגל</h1>
          <p className="mx-auto mt-4 max-w-2xl text-white/70">
            חיזוי מדויק על בסיס 5 משחקים אחרונים, היסטוריית H2H, וסימולציית Poisson.
            הניתוח בעברית עם נתונים מ-API-Football.
          </p>
        </header>

        <form
          onSubmit={handleSubmit}
          className="mx-auto mb-6 max-w-4xl rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur"
        >
          <div className="grid gap-4 md:grid-cols-[1fr_auto_1fr_auto] md:items-end">
            <label className="block text-right">
              <span className="mb-2 block text-sm text-white/60">קבוצה 1</span>
              <input
                value={team1}
                onChange={(e) => setTeam1(e.target.value)}
                className="w-full rounded-xl border border-white/10 bg-pitch-950 px-4 py-3 text-right outline-none ring-gold focus:ring-2"
                placeholder="ברזיל"
              />
            </label>

            <div className="hidden pb-3 text-center text-xl text-gold md:block">⚽</div>

            <label className="block text-right">
              <span className="mb-2 block text-sm text-white/60">קבוצה 2</span>
              <input
                value={team2}
                onChange={(e) => setTeam2(e.target.value)}
                className="w-full rounded-xl border border-white/10 bg-pitch-950 px-4 py-3 text-right outline-none ring-gold focus:ring-2"
                placeholder="צרפת"
              />
            </label>

            <button
              type="submit"
              disabled={loading}
              className="rounded-xl bg-gold px-8 py-3 font-bold text-pitch-950 transition hover:brightness-110 disabled:opacity-60"
            >
              {loading ? "מנתח..." : "נתח משחק"}
            </button>
          </div>
        </form>

        <div className="mx-auto mb-8 flex max-w-4xl flex-wrap justify-center gap-2">
          {POPULAR_MATCHES.map(([a, b]) => (
            <button
              key={`${a}-${b}`}
              type="button"
              onClick={() => {
                setTeam1(a);
                setTeam2(b);
                analyze(a, b);
              }}
              className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm transition hover:border-gold/40 hover:bg-gold/10"
            >
              {a} נגד {b}
            </button>
          ))}
        </div>

        {error && (
          <div className="mx-auto mb-8 max-w-4xl rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-red-200">
            {error}
          </div>
        )}

        {result && (
          <section className="mx-auto max-w-6xl space-y-6">
            <div className="rounded-xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-white/70">
              📡 איכות נתונים: <span className="text-gold">{result.data_quality}</span>
              {result.has_live_data && (
                <span className="mr-3 text-green-400"> • נתונים live מה-API</span>
              )}
            </div>

            <div className="grid gap-6 lg:grid-cols-2">
              <div className="rounded-2xl border border-white/10 bg-white/5 p-6">
                <h2 className="mb-2 text-2xl font-bold">{result.match}</h2>
                <p className="mb-6 text-white/70">{result.summary}</p>

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
                    <div key={item.name} className="rounded-lg bg-black/30 p-3">
                      <div
                        className="mx-auto mb-2 h-2 w-8 rounded-full"
                        style={{ backgroundColor: COLORS[index] }}
                      />
                      <p className="text-white/60">{item.name}</p>
                      <p className="text-xl font-bold">{item.value}%</p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="space-y-4">
                <div className="rounded-2xl border border-white/10 bg-white/5 p-6">
                  <h3 className="mb-3 text-lg font-semibold">🎯 שערים צפויים (xG)</h3>
                  <div className="space-y-2">
                    {Object.entries(result.expected_goals).map(([team, xg]) => (
                      <div
                        key={team}
                        className="flex items-center justify-between rounded-lg bg-black/30 px-4 py-3"
                      >
                        <span className="font-medium">{team}</span>
                        <span className="text-2xl font-bold text-gold">{xg}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="rounded-2xl border border-gold/30 bg-gold/10 p-6">
                  <h3 className="mb-2 text-lg font-bold text-gold">💡 המלצה</h3>
                  <p className="text-lg">{result.recommendation}</p>
                  <p className="mt-2 text-sm text-white/70">
                    סיכון אפסט: <strong>{result.upset_risk}</strong>
                  </p>
                </div>
              </div>
            </div>

            <div className="rounded-2xl border border-white/10 bg-white/5 p-6">
              <h3 className="mb-4 text-xl font-semibold">🔍 ניתוח מפורט</h3>
              <p className="mb-4 leading-relaxed text-white/85">{result.detailed}</p>
              <ul className="space-y-3">
                {result.analysis.map((point, index) => (
                  <li
                    key={index}
                    className="rounded-lg bg-black/20 px-4 py-3 text-white/90"
                  >
                    {point}
                  </li>
                ))}
              </ul>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              {Object.entries(result.recent_form).map(([team, matches]) => (
                <div
                  key={team}
                  className="rounded-2xl border border-white/10 bg-white/5 p-5"
                >
                  <h4 className="mb-3 font-semibold">📈 5 משחקים אחרונים — {team}</h4>
                  {matches.length > 0 ? (
                    <ul className="space-y-2 text-sm text-white/80">
                      {matches.map((m, i) => (
                        <li key={i} className="rounded bg-black/20 px-3 py-2">
                          {m}
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-sm text-white/50">
                      אין נתונים — ודא ש-FOOTBALL_DATA_API_KEY מוגדר ב-GitHub
                    </p>
                  )}
                </div>
              ))}
            </div>

            {result.head_to_head.length > 0 && (
              <div className="rounded-2xl border border-white/10 bg-white/5 p-6">
                <h3 className="mb-2 text-lg font-semibold">🔄 היסטוריית מפגשים (H2H)</h3>
                <p className="mb-3 text-gold">{result.h2h_summary}</p>
                <ul className="space-y-2 text-sm">
                  {result.head_to_head.map((m, i) => (
                    <li key={i} className="rounded bg-black/20 px-3 py-2 text-white/80">
                      {m}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {(result.market_odds?.odds || result.weather) && (
              <div className="grid gap-4 md:grid-cols-2">
                {result.market_odds?.odds && (
                  <div className="rounded-2xl border border-white/10 bg-white/5 p-5">
                    <h4 className="mb-3 font-semibold">💰 יחסי שוק (Odds API)</h4>
                    <ul className="space-y-1 text-sm">
                      {Object.entries(result.market_odds.odds).map(([name, price]) => (
                        <li key={name} className="flex justify-between rounded bg-black/20 px-3 py-2">
                          <span>{name}</span>
                          <span className="font-bold text-gold">{price}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                {result.weather && (
                  <div className="rounded-2xl border border-white/10 bg-white/5 p-5">
                    <h4 className="mb-3 font-semibold">🌤️ מזג אוויר</h4>
                    <p className="text-sm text-white/80">
                      {result.weather.city}: {result.weather.description}, {result.weather.temp_c}°C
                    </p>
                    <p className="mt-2 text-sm text-gold">{result.weather.impact_he}</p>
                  </div>
                )}
              </div>
            )}
          </section>
        )}
      </div>
    </main>
  );
}
