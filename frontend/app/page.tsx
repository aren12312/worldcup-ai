"use client";

import { FormEvent, useState } from "react";
import { AnalysisDashboard, Prediction } from "./components/AnalysisDashboard";
import { TeamAutocomplete } from "./components/TeamAutocomplete";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";

const QUICK = [
  ["ברזיל", "צרפת"],
  ["ארגנטינה", "אנגליה"],
  ["ספרד", "גרמניה"],
  ["פורטוגל", "הולנד"],
];

const FEATURES = [
  { icon: "📊", title: "הסתברויות מדויקות", desc: "Poisson + 10,000 סימולציות Monte Carlo" },
  { icon: "📈", title: "סטטיסטיקות pro", desc: "טופס, H2H, xG, Over/BTTS" },
  { icon: "⭐", title: "שחקני מפתח", desc: "זמינות, פציעות והשפעה על המשחק" },
  { icon: "📋", title: "דוח אנליטי", desc: "דוח מקצועי להדפסה — מעבר ל-Predigoal" },
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
      const res = await fetch(`${API_URL}/predict?${params}`);
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "הניתוח נכשל");
      setResult(data);
      setTimeout(() => document.getElementById("results")?.scrollIntoView({ behavior: "smooth" }), 100);
    } catch (e) {
      setError(e instanceof Error ? e.message : "שגיאה");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main dir="rtl" className="min-h-screen">
      {/* Hero */}
      <section className="relative overflow-hidden border-b border-white/5">
        <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-emerald-900/30 via-pitch-950 to-pitch-950" />
        <div className="relative mx-auto max-w-6xl px-4 py-16 md:py-24">
          <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-4 py-1.5 text-sm text-emerald-300">
            <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-400" />
            WorldCup AI — ברמה מעל Predigoal
          </div>

          <h1 className="max-w-3xl text-4xl font-extrabold leading-tight md:text-6xl">
            נתח כל משחק מונדיאל
            <span className="block text-gold"> עם AI מקצועי</span>
          </h1>
          <p className="mt-5 max-w-2xl text-lg text-white/60">
            סטטיסטיקות live, H2H, שחקני מפתח, xG, יחסי שוק ודוח אנליטי מלא — בעברית.
          </p>

          <form
            onSubmit={(e: FormEvent) => { e.preventDefault(); analyze(team1, team2); }}
            className="mt-10 glass glow-gold rounded-3xl p-6 md:p-8"
          >
            <div className="grid gap-4 md:grid-cols-[1fr_auto_1fr_auto] md:items-end">
              <TeamAutocomplete value={team1} onChange={setTeam1} label="קבוצה ביתית" placeholder="ברזיל" />
              <div className="hidden pb-4 text-2xl text-white/30 md:block">VS</div>
              <TeamAutocomplete value={team2} onChange={setTeam2} label="קבוצה אורחת" placeholder="צרפת" />
              <button
                type="submit"
                disabled={loading}
                className="flex items-center justify-center gap-2 rounded-2xl bg-gradient-to-l from-gold to-amber-400 px-8 py-4 font-bold text-pitch-950 transition hover:brightness-110 disabled:opacity-50"
              >
                {loading ? (
                  <><span className="h-5 w-5 animate-spin rounded-full border-2 border-pitch-950/30 border-t-pitch-950" /> מנתח...</>
                ) : (
                  <>⚡ נתח עם AI</>
                )}
              </button>
            </div>
          </form>

          <div className="mt-4 flex flex-wrap gap-2">
            {QUICK.map(([a, b]) => (
              <button
                key={`${a}-${b}`}
                type="button"
                onClick={() => { setTeam1(a); setTeam2(b); analyze(a, b); }}
                className="rounded-full glass px-4 py-2 text-sm transition hover:border-gold/30 hover:bg-gold/5"
              >
                {a} נגד {b}
              </button>
            ))}
          </div>

          {error && (
            <div className="mt-4 rounded-2xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-red-200">{error}</div>
          )}

          <div className="mt-8 flex flex-wrap gap-6 text-sm text-white/40">
            <a href="https://t.me/WorldCupApi" target="_blank" rel="noreferrer" className="hover:text-gold">📱 @WorldCupApi</a>
            <span>•</span>
            <span>50+ נבחרות</span>
            <span>•</span>
            <span>דוח להדפסה</span>
          </div>
        </div>
      </section>

      {/* Features */}
      {!result && (
        <section className="mx-auto max-w-6xl px-4 py-16">
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {FEATURES.map((f) => (
              <div key={f.title} className="glass rounded-2xl p-6 transition hover:border-gold/20">
                <span className="text-3xl">{f.icon}</span>
                <h3 className="mt-3 font-semibold">{f.title}</h3>
                <p className="mt-2 text-sm text-white/50">{f.desc}</p>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Results */}
      {result && (
        <div id="results" className="mx-auto max-w-6xl px-4 py-12">
          <AnalysisDashboard data={result} />
        </div>
      )}

      <footer className="border-t border-white/5 py-8 text-center text-sm text-white/30">
        WorldCup AI © 2026 • ניתוח לצורכי מידע בלבד
      </footer>
    </main>
  );
}
