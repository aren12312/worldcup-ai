"use client";

import { FormEvent, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { AnalysisDashboard, Prediction } from "./components/AnalysisDashboard";
import { TeamAutocomplete } from "./components/TeamAutocomplete";
import { LoadingSkeleton } from "./components/LoadingSkeleton";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";

const QUICK = [
  ["ברזיל", "צרפת"],
  ["ארגנטינה", "אנגליה"],
  ["ספרד", "גרמניה"],
  ["פורטוגל", "הולנד"],
];

const FEATURES = [
  { icon: "🧪", title: "סימולטור שחקנים", desc: "מה אם כוכב לא ישחק? הרצה מחדש בזמן אמת" },
  { icon: "💎", title: "מנוע ערך מול השוק", desc: "Edge, יחסים הוגנים והמלצת Kelly" },
  { icon: "🔥", title: "מפת חום תוצאות", desc: "מודל Dixon-Coles לכל תוצאה אפשרית" },
  { icon: "📈", title: "מומנטום חי", desc: "הסתברות ניצחון דקה-אחר-דקה עם תרחישים" },
];

async function fetchPrediction(t1: string, t2: string): Promise<Prediction> {
  const params = new URLSearchParams({ team1: t1, team2: t2, lang: "he" });
  const res = await fetch(`${API_URL}/predict?${params}`);
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "הניתוח נכשל");
  return data;
}

export default function Home() {
  const [team1, setTeam1] = useState("ברזיל");
  const [team2, setTeam2] = useState("צרפת");
  const [query, setQuery] = useState<{ t1: string; t2: string } | null>(null);

  const { data: result, isFetching, error } = useQuery({
    queryKey: ["predict", query?.t1, query?.t2],
    queryFn: () => fetchPrediction(query!.t1, query!.t2),
    enabled: !!query,
  });

  function analyze(t1: string, t2: string) {
    setTeam1(t1);
    setTeam2(t2);
    setQuery({ t1, t2 });
    setTimeout(() => document.getElementById("results")?.scrollIntoView({ behavior: "smooth" }), 120);
  }

  return (
    <main dir="rtl" className="min-h-screen">
      <section className="relative overflow-hidden border-b border-white/5">
        <div className="pointer-events-none absolute inset-0 bg-grid-faint [background-size:40px_40px] opacity-40" />
        <div className="relative mx-auto max-w-6xl px-4 py-16 md:py-24">
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-4 inline-flex items-center gap-2 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-4 py-1.5 text-sm text-emerald-300"
          >
            <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-400" />
            מנוע אנליטי דור הבא — Dixon-Coles • Monte Carlo • Value AI
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.05 }}
            className="max-w-3xl text-4xl font-extrabold leading-tight md:text-6xl"
          >
            נתח כל משחק מונדיאל
            <span className="block gradient-text">ברמת אנליסט מקצועי</span>
          </motion.h1>
          <p className="mt-5 max-w-2xl text-lg text-white/60">
            סימולציה אינטראקטיבית, מנוע ערך מול שוק ההימורים, השפעת שחקנים והסבר מלא לכל חיזוי — בעברית.
          </p>

          <motion.form
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            onSubmit={(e: FormEvent) => { e.preventDefault(); analyze(team1, team2); }}
            className="mt-10 glass-strong glow-gold rounded-3xl p-6 md:p-8"
          >
            <div className="grid gap-4 md:grid-cols-[1fr_auto_1fr_auto] md:items-end">
              <TeamAutocomplete value={team1} onChange={setTeam1} label="קבוצה ביתית" placeholder="ברזיל" />
              <div className="hidden pb-4 text-2xl text-white/30 md:block">VS</div>
              <TeamAutocomplete value={team2} onChange={setTeam2} label="קבוצה אורחת" placeholder="צרפת" />
              <button
                type="submit"
                disabled={isFetching}
                className="flex items-center justify-center gap-2 rounded-2xl bg-gradient-to-l from-gold to-amber-400 px-8 py-4 font-bold text-pitch-950 transition hover:brightness-110 disabled:opacity-50"
              >
                {isFetching ? (
                  <><span className="h-5 w-5 animate-spin rounded-full border-2 border-pitch-950/30 border-t-pitch-950" /> מנתח...</>
                ) : (
                  <>⚡ נתח עם AI</>
                )}
              </button>
            </div>
          </motion.form>

          <div className="mt-4 flex flex-wrap gap-2">
            {QUICK.map(([a, b]) => (
              <button
                key={`${a}-${b}`}
                type="button"
                onClick={() => analyze(a, b)}
                className="rounded-full glass px-4 py-2 text-sm transition hover:border-gold/30 hover:bg-gold/5"
              >
                {a} נגד {b}
              </button>
            ))}
          </div>

          {error && (
            <div className="mt-4 rounded-2xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-red-200">
              {error instanceof Error ? error.message : "שגיאה"}
            </div>
          )}

          <div className="mt-8 flex flex-wrap gap-6 text-sm text-white/40">
            <a href="https://t.me/WorldCupApi" target="_blank" rel="noreferrer" className="hover:text-gold">📱 @WorldCupApi</a>
            <span>•</span>
            <span>50+ נבחרות</span>
            <span>•</span>
            <span>מודל Dixon-Coles</span>
          </div>
        </div>
      </section>

      {!result && !isFetching && (
        <section className="mx-auto max-w-6xl px-4 py-16">
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {FEATURES.map((f, i) => (
              <motion.div
                key={f.title}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.06 }}
                className="glass card-hover rounded-2xl p-6"
              >
                <span className="text-3xl">{f.icon}</span>
                <h3 className="mt-3 font-semibold">{f.title}</h3>
                <p className="mt-2 text-sm text-white/50">{f.desc}</p>
              </motion.div>
            ))}
          </div>
        </section>
      )}

      <div id="results" className="mx-auto max-w-6xl px-4 py-12">
        {isFetching && <LoadingSkeleton />}
        {!isFetching && result && <AnalysisDashboard data={result} />}
      </div>

      <footer className="border-t border-white/5 py-8 text-center text-sm text-white/30">
        WorldCup AI © 2026 • ניתוח לצורכי מידע בלבד • לא ייעוץ פיננסי
      </footer>
    </main>
  );
}
