"use client";

import { useEffect, useMemo } from "react";
import { motion } from "framer-motion";
import { probabilities } from "../lib/sim";
import { useSimStore, SimParams } from "../lib/store";

type KeyPlayer = { name: string; role: string; impact: number; status: string; status_label: string };

function Delta({ value }: { value: number }) {
  if (Math.abs(value) < 0.1) return <span className="text-white/40">±0</span>;
  const up = value > 0;
  return (
    <span className={up ? "text-emerald-400" : "text-red-400"}>
      {up ? "▲" : "▼"} {Math.abs(value).toFixed(1)}
    </span>
  );
}

export function PlayerImpactSimulator({
  simParams,
  keyPlayers,
  baseProbs,
}: {
  simParams: SimParams;
  keyPlayers: Record<string, KeyPlayer[]>;
  baseProbs: { team1_win: number; draw: number; team2_win: number };
}) {
  const { setBase, togglePlayer, out, reset, adjustedXg } = useSimStore();

  useEffect(() => {
    setBase(simParams);
  }, [simParams, setBase]);

  const teams = [simParams.team1, simParams.team2];
  const adj = adjustedXg();
  const live = useMemo(() => probabilities(adj.t1, adj.t2, simParams.rho), [adj.t1, adj.t2, simParams.rho]);
  const outCount = Object.keys(out).length;

  const rows = [
    { label: simParams.team1, base: baseProbs.team1_win, now: live.team1Win, color: "#10b981" },
    { label: "תיקו", base: baseProbs.draw, now: live.draw, color: "#64748b" },
    { label: simParams.team2, base: baseProbs.team2_win, now: live.team2Win, color: "#f5c542" },
  ];

  return (
    <div className="glass-strong rounded-3xl p-6">
      <div className="mb-1 flex items-center justify-between">
        <h3 className="font-semibold">🧪 סימולטור &quot;מה אם שחקן לא ישחק?&quot;</h3>
        {outCount > 0 && (
          <button onClick={reset} className="text-xs text-white/50 hover:text-white">
            אפס ({outCount})
          </button>
        )}
      </div>
      <p className="mb-5 text-xs text-white/50">
        סמן שחקנים שלא ישחקו — המודל מריץ סימולציה מחדש בזמן אמת ומציג את שינוי ההסתברות.
      </p>

      <div className="mb-6 grid grid-cols-3 gap-3">
        {rows.map((r) => (
          <div key={r.label} className="rounded-2xl bg-black/30 p-4 text-center">
            <div className="mx-auto mb-2 h-1 w-8 rounded-full" style={{ background: r.color }} />
            <p className="truncate text-xs text-white/50">{r.label}</p>
            <motion.p key={r.now} initial={{ scale: 1.15 }} animate={{ scale: 1 }} className="text-2xl font-bold">
              {r.now}%
            </motion.p>
            <p className="text-xs"><Delta value={r.now - r.base} /></p>
          </div>
        ))}
      </div>

      <div className="grid gap-5 md:grid-cols-2">
        {teams.map((team, ti) => (
          <div key={team}>
            <h4 className="mb-3 text-sm font-medium text-white/70">{team}</h4>
            <div className="flex flex-wrap gap-2">
              {(keyPlayers[team] || []).map((p) => {
                const key = `${team}:${p.name}`;
                const isOut = !!out[key];
                return (
                  <button
                    key={key}
                    onClick={() => togglePlayer(key, { name: p.name, team: (ti + 1) as 1 | 2, impact: p.impact })}
                    className={`flex items-center gap-2 rounded-full border px-3 py-1.5 text-xs transition ${
                      isOut
                        ? "border-red-400/60 bg-red-400/15 text-red-200 line-through"
                        : "border-white/10 bg-white/5 hover:border-gold/40"
                    }`}
                  >
                    <span>{p.name}</span>
                    <span className="text-[10px] text-white/40">{p.impact}</span>
                  </button>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {outCount > 0 && (
        <p className="mt-5 rounded-xl bg-black/30 px-4 py-3 text-xs text-white/60">
          xG מתואם: {simParams.team1} {adj.t1.toFixed(2)} | {simParams.team2} {adj.t2.toFixed(2)}
        </p>
      )}
    </div>
  );
}
