"use client";

import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import {
  Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";
import { ScorelineHeatmap } from "./ScorelineHeatmap";
import { ExplainabilityWaterfall } from "./ExplainabilityWaterfall";
import { ValuePanel, ValueAnalysis } from "./ValuePanel";
import { TacticalRadar } from "./TacticalRadar";
import { MomentumTimeline } from "./MomentumTimeline";
import { PlayerImpactSimulator } from "./PlayerImpactSimulator";
import { SimParams } from "../lib/store";

type Band = { low: number; mid: number; high: number };

export type Prediction = {
  match: string;
  confidence: number;
  probabilities: Record<string, number>;
  labels: { team1: string; team2: string; draw: string };
  expected_goals: Record<string, number>;
  xg_breakdown: Record<string, { xg: number; factors: { label: string; value: number }[] }>;
  scorelines: { score: string; probability: number }[];
  scoreline_grid: number[][];
  probability_bands?: { team1_win: Band; draw: Band; team2_win: Band } | null;
  value_analysis?: ValueAnalysis | null;
  sim_params: SimParams;
  summary: string;
  detailed: string;
  analysis: string[];
  recommendation: string;
  upset_risk: string;
  data_quality: string;
  has_live_data: boolean;
  recent_form: Record<string, string[]>;
  head_to_head: string[];
  h2h_summary: string;
  key_players: Record<string, Array<{
    name: string; role: string; impact: number; status: string;
    status_label: string; note: string;
  }>>;
  team_comparison: {
    metrics: Record<string, { label: string; team1: number; team2: number }>;
  };
  report: {
    sections: { title: string; content: string }[];
    scorelines: { score: string; probability: number }[];
  };
  market_odds?: { odds?: Record<string, number> } | null;
  weather?: { city?: string; description?: string; temp_c?: number; impact_he?: string } | null;
};

const TABS = ["סקירה", "סימולטור", "מודל", "סטטיסטיקה", "ערך", "H2H", "שחקנים", "דוח"] as const;
const COLORS = ["#10b981", "#64748b", "#f5c542"];
const STATUS_COLOR: Record<string, string> = {
  available: "text-emerald-400 bg-emerald-400/10",
  doubtful: "text-amber-400 bg-amber-400/10",
  injured: "text-red-400 bg-red-400/10",
  suspended: "text-orange-400 bg-orange-400/10",
};

export function AnalysisDashboard({ data }: { data: Prediction }) {
  const [tab, setTab] = useState<(typeof TABS)[number]>("סקירה");

  const t1 = data.labels.team1;
  const t2 = data.labels.team2;
  const bands = data.probability_bands;

  const probChart = [
    { name: t1, value: data.probabilities.team1_win, fill: COLORS[0] },
    { name: data.labels.draw, value: data.probabilities.draw, fill: COLORS[1] },
    { name: t2, value: data.probabilities.team2_win, fill: COLORS[2] },
  ];

  return (
    <section className="space-y-6">
      {/* Header card */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-strong glow-gold rounded-3xl p-6 md:p-8"
      >
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-sm text-gold">דוח אנליטי • Dixon-Coles + Monte Carlo</p>
            <h2 className="mt-1 text-3xl font-bold md:text-4xl">{data.match}</h2>
            <p className="mt-3 max-w-2xl text-white/70">{data.summary}</p>
          </div>
          <div className="text-center">
            <div className="relative mx-auto flex h-24 w-24 items-center justify-center rounded-full border-4 border-gold/30 bg-gold/5">
              <span className="text-3xl font-bold text-gold">{data.confidence}</span>
            </div>
            <p className="mt-2 text-xs text-white/50">ציון ביטחון</p>
          </div>
        </div>

        <div className="mt-6 grid grid-cols-2 gap-3 md:grid-cols-5">
          {[
            [t1, `${data.probabilities.team1_win}%`, COLORS[0], bands?.team1_win],
            ["תיקו", `${data.probabilities.draw}%`, COLORS[1], bands?.draw],
            [t2, `${data.probabilities.team2_win}%`, COLORS[2], bands?.team2_win],
            ["Over 2.5", `${data.probabilities.over_2_5 ?? "-"}%`, "#a855f7", null],
            ["BTTS", `${data.probabilities.btts_yes ?? "-"}%`, "#f97316", null],
          ].map(([label, val, color, band]) => (
            <div key={String(label)} className="rounded-2xl bg-black/30 p-4 text-center">
              <div className="mx-auto mb-2 h-1 w-8 rounded-full" style={{ background: String(color) }} />
              <p className="truncate text-xs text-white/50">{label as string}</p>
              <p className="text-xl font-bold">{val as string}</p>
              {band && (
                <p className="mt-0.5 text-[10px] text-white/40">
                  {(band as Band).low}–{(band as Band).high}%
                </p>
              )}
            </div>
          ))}
        </div>
      </motion.div>

      {/* Tabs */}
      <div className="no-print -mx-1 flex gap-2 overflow-x-auto px-1 pb-1">
        {TABS.map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`tab-pill shrink-0 ${tab === t ? "bg-gold text-pitch-950" : "glass hover:bg-white/10"}`}
          >
            {t}
          </button>
        ))}
        <button
          onClick={() => window.print()}
          className="tab-pill mr-auto shrink-0 glass hover:bg-white/10"
        >
          🖨️ הדפס
        </button>
      </div>

      <AnimatePresence mode="wait">
        <motion.div
          key={tab}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -8 }}
          transition={{ duration: 0.2 }}
        >
          {tab === "סקירה" && (
            <div className="grid gap-6 lg:grid-cols-2">
              <div className="glass rounded-3xl p-6">
                <h3 className="mb-4 font-semibold">הסתברויות</h3>
                <div className="h-56">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={probChart} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" />
                      <XAxis type="number" domain={[0, 100]} tick={{ fill: "#ffffff80", fontSize: 12 }} />
                      <YAxis type="category" dataKey="name" width={80} tick={{ fill: "#fff", fontSize: 12 }} />
                      <Tooltip formatter={(v: number) => `${v}%`} contentStyle={{ background: "#0a1410", border: "1px solid #ffffff20", borderRadius: 12 }} />
                      <Bar dataKey="value" radius={[0, 8, 8, 0]}>
                        {probChart.map((e, i) => <Cell key={i} fill={e.fill} />)}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
                {bands && (
                  <p className="mt-2 text-xs text-white/40">
                    רצועות ביטחון (10–90%) מציגות את אי-הוודאות של המודל.
                  </p>
                )}
              </div>

              <div className="space-y-4">
                <div className="glass rounded-3xl p-6">
                  <h3 className="mb-3 font-semibold">🎯 xG & תוצאות סבירות</h3>
                  <div className="mb-4 grid grid-cols-2 gap-3">
                    {Object.entries(data.expected_goals).map(([team, xg]) => (
                      <div key={team} className="rounded-xl bg-black/30 p-4 text-center">
                        <p className="truncate text-sm text-white/50">{team}</p>
                        <p className="text-3xl font-bold text-gold">{xg}</p>
                        <p className="text-xs text-white/40">שערים צפויים</p>
                      </div>
                    ))}
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {data.scorelines.map((s) => (
                      <span key={s.score} className="rounded-lg bg-black/30 px-3 py-1.5 text-sm">
                        {s.score} <span className="text-gold">{s.probability}%</span>
                      </span>
                    ))}
                  </div>
                </div>

                <div className="rounded-3xl border border-gold/30 bg-gold/10 p-6">
                  <h3 className="font-bold text-gold">💡 {data.recommendation}</h3>
                  <p className="mt-2 text-sm text-white/70">סיכון אפסט: {data.upset_risk}</p>
                </div>
              </div>

              <div className="glass lg:col-span-2 rounded-3xl p-6">
                <h3 className="mb-4 font-semibold">ניתוח AI</h3>
                <p className="mb-4 leading-relaxed text-white/85">{data.detailed}</p>
                <div className="grid gap-2 md:grid-cols-2">
                  {data.analysis.map((a, i) => (
                    <div key={i} className="rounded-xl bg-black/25 px-4 py-3 text-sm">{a}</div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {tab === "סימולטור" && (
            <div className="space-y-6">
              <PlayerImpactSimulator
                simParams={data.sim_params}
                keyPlayers={data.key_players}
                baseProbs={{
                  team1_win: data.probabilities.team1_win,
                  draw: data.probabilities.draw,
                  team2_win: data.probabilities.team2_win,
                }}
              />
              <MomentumTimeline
                t1xg={data.sim_params.team1_xg}
                t2xg={data.sim_params.team2_xg}
                team1={t1}
                team2={t2}
              />
            </div>
          )}

          {tab === "מודל" && (
            <div className="space-y-6">
              <ScorelineHeatmap grid={data.scoreline_grid} team1={t1} team2={t2} />
              <div className="grid gap-6 md:grid-cols-2">
                {Object.entries(data.xg_breakdown).map(([team, b]) => (
                  <ExplainabilityWaterfall key={team} team={team} xg={b.xg} factors={b.factors} />
                ))}
              </div>
            </div>
          )}

          {tab === "סטטיסטיקה" && (
            <div className="space-y-6">
              <div className="grid gap-6 lg:grid-cols-2">
                <TacticalRadar metrics={data.team_comparison.metrics} team1={t1} team2={t2} />
                <div className="glass rounded-3xl p-6">
                  <h3 className="mb-6 font-semibold">השוואת קבוצות</h3>
                  <div className="space-y-6">
                    {Object.entries(data.team_comparison.metrics).map(([key, m]) => {
                      const max = Math.max(m.team1, m.team2, 1);
                      return (
                        <div key={key}>
                          <div className="mb-2 flex justify-between text-sm">
                            <span>{t1}: <strong>{m.team1}</strong></span>
                            <span className="text-white/50">{m.label}</span>
                            <span><strong>{m.team2}</strong> :{t2}</span>
                          </div>
                          <div className="grid grid-cols-2 gap-2">
                            <div className="stat-bar"><div className="stat-fill" style={{ width: `${(m.team1 / max) * 100}%` }} /></div>
                            <div className="stat-bar"><div className="stat-fill ml-auto" style={{ width: `${(m.team2 / max) * 100}%`, marginRight: 0, marginLeft: "auto" }} /></div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                {Object.entries(data.recent_form).map(([team, matches]) => (
                  <div key={team} className="glass rounded-2xl p-5">
                    <h4 className="mb-3 font-medium">📈 {team} — 5 אחרונים</h4>
                    {matches.length > 0 ? matches.map((m, i) => (
                      <div key={i} className="mb-2 rounded-lg bg-black/30 px-3 py-2 text-sm">{m}</div>
                    )) : (
                      <p className="text-sm text-white/40">אין נתונים</p>
                    )}
                  </div>
                ))}
              </div>
              <p className="text-xs text-white/40">📡 {data.data_quality}</p>
            </div>
          )}

          {tab === "ערך" && (
            <div className="space-y-6">
              {data.value_analysis ? (
                <ValuePanel data={data.value_analysis} />
              ) : (
                <div className="glass rounded-3xl p-8 text-center text-white/60">
                  <p className="text-lg">💎 מנוע ערך מול השוק</p>
                  <p className="mt-2 text-sm">אין כרגע יחסי שוק זמינים למשחק זה (נדרש מפתח Odds API פעיל ומשחק עם שוק פתוח).</p>
                </div>
              )}
              {data.weather && (
                <div className="glass rounded-3xl p-6">
                  <h3 className="mb-2 font-semibold">🌤️ תנאי מזג אוויר</h3>
                  <p className="text-white/70">
                    {data.weather.city}: {data.weather.description}, {data.weather.temp_c}°C — {data.weather.impact_he}
                  </p>
                </div>
              )}
            </div>
          )}

          {tab === "H2H" && (
            <div className="glass rounded-3xl p-6">
              <h3 className="mb-2 font-semibold">🔄 היסטוריית מפגשים</h3>
              <p className="mb-6 text-gold">{data.h2h_summary}</p>
              {data.head_to_head.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-white/10 text-white/50">
                        <th className="py-3 text-right">תאריך</th>
                        <th className="py-3 text-right">משחק</th>
                        <th className="py-3 text-right">תוצאה</th>
                        <th className="py-3 text-right">תחרות</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.head_to_head.map((row, i) => {
                        const parts = row.split("|").map((p) => p.trim());
                        return (
                          <tr key={i} className="border-b border-white/5 hover:bg-white/5">
                            <td className="py-3">{parts[0]}</td>
                            <td className="py-3">{parts[1]?.replace(parts[2] || "", "").trim()}</td>
                            <td className="py-3 font-bold text-gold">{parts[1]?.match(/\d+-\d+/)?.[0]}</td>
                            <td className="py-3 text-white/60">{parts[2]?.replace(/^\d+-\d+\s*/, "")}</td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="text-white/50">אין נתוני H2H</p>
              )}
            </div>
          )}

          {tab === "שחקנים" && (
            <div className="grid gap-6 md:grid-cols-2">
              {[t1, t2].map((team) => (
                <div key={team} className="glass rounded-3xl p-6">
                  <h3 className="mb-4 font-semibold">⭐ שחקני מפתח — {team}</h3>
                  <div className="space-y-3">
                    {(data.key_players[team] || []).map((p) => (
                      <div key={p.name} className="rounded-2xl bg-black/25 p-4">
                        <div className="flex items-start justify-between gap-2">
                          <div>
                            <p className="font-semibold">{p.name}</p>
                            <p className="text-xs text-white/50">{p.role}</p>
                          </div>
                          <span className={`rounded-full px-2 py-0.5 text-xs ${STATUS_COLOR[p.status] || ""}`}>
                            {p.status_label}
                          </span>
                        </div>
                        <div className="mt-2 flex items-center gap-2">
                          <div className="stat-bar flex-1"><div className="stat-fill" style={{ width: `${p.impact}%` }} /></div>
                          <span className="text-xs text-gold">{p.impact}</span>
                        </div>
                        <p className="mt-2 text-xs text-white/60">{p.note}</p>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}

          {tab === "דוח" && (
            <div className="glass print-only rounded-3xl p-8">
              <div className="mb-8 border-b border-white/10 pb-6">
                <h2 className="text-2xl font-bold">דוח אנליטי מקצועי</h2>
                <p className="text-white/60">{data.match} • ביטחון {data.confidence}/100</p>
              </div>
              {data.report.sections.map((s, i) => (
                <div key={i} className="mb-6">
                  <h3 className="mb-2 font-semibold text-gold">{s.title}</h3>
                  <p className="leading-relaxed text-white/85">{s.content}</p>
                </div>
              ))}
              <h3 className="mb-3 font-semibold">תוצאות סבירות</h3>
              <div className="flex flex-wrap gap-2">
                {data.report.scorelines.map((s) => (
                  <span key={s.score} className="rounded-lg bg-black/30 px-3 py-1">{s.score}: {s.probability}%</span>
                ))}
              </div>
            </div>
          )}
        </motion.div>
      </AnimatePresence>
    </section>
  );
}
