"use client";

import { useMemo, useState } from "react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { momentumTimeline } from "../lib/sim";

type WhatIfEvent = { minute: number; team: 1 | 2; type: "goal" | "red" };

export function MomentumTimeline({
  t1xg,
  t2xg,
  team1,
  team2,
}: {
  t1xg: number;
  t2xg: number;
  team1: string;
  team2: string;
}) {
  const [events, setEvents] = useState<WhatIfEvent[]>([]);

  const data = useMemo(
    () => momentumTimeline(t1xg, t2xg, events).map((p) => ({ ...p, name: `${p.minute}'` })),
    [t1xg, t2xg, events]
  );

  const addEvent = (e: WhatIfEvent) => setEvents((prev) => [...prev, e]);

  const buttons: { label: string; e: WhatIfEvent }[] = [
    { label: `⚽ גול ל${team1} (15')`, e: { minute: 15, team: 1, type: "goal" } },
    { label: `⚽ גול ל${team2} (15')`, e: { minute: 15, team: 2, type: "goal" } },
    { label: `🟥 אדום ל${team1} (40')`, e: { minute: 40, team: 1, type: "red" } },
    { label: `🟥 אדום ל${team2} (40')`, e: { minute: 40, team: 2, type: "red" } },
  ];

  return (
    <div className="glass rounded-3xl p-6">
      <div className="mb-1 flex items-center justify-between">
        <h3 className="font-semibold">📈 סימולציית מומנטום</h3>
        {events.length > 0 && (
          <button onClick={() => setEvents([])} className="text-xs text-white/50 hover:text-white">
            איפוס תרחיש
          </button>
        )}
      </div>
      <p className="mb-4 text-xs text-white/50">הסתברות ניצחון לאורך 90 דקות — נסה תרחישי &quot;מה אם&quot;</p>

      <div className="h-60">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} stackOffset="expand">
            <defs>
              <linearGradient id="g1" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#10b981" stopOpacity={0.7} />
                <stop offset="100%" stopColor="#10b981" stopOpacity={0.1} />
              </linearGradient>
              <linearGradient id="g2" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#f5c542" stopOpacity={0.7} />
                <stop offset="100%" stopColor="#f5c542" stopOpacity={0.1} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" />
            <XAxis dataKey="name" tick={{ fill: "#ffffff70", fontSize: 11 }} interval={2} />
            <YAxis tickFormatter={(v) => `${Math.round(v * 100)}%`} tick={{ fill: "#ffffff70", fontSize: 11 }} />
            <Tooltip
              formatter={(v: number, n: string) => [`${Math.round(v)}%`, n]}
              contentStyle={{ background: "#0a1410", border: "1px solid #ffffff20", borderRadius: 12 }}
            />
            <Area type="monotone" dataKey="team1" name={team1} stackId="1" stroke="#10b981" fill="url(#g1)" />
            <Area type="monotone" dataKey="draw" name="תיקו" stackId="1" stroke="#64748b" fill="#64748b40" />
            <Area type="monotone" dataKey="team2" name={team2} stackId="1" stroke="#f5c542" fill="url(#g2)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        {buttons.map((b) => (
          <button
            key={b.label}
            onClick={() => addEvent(b.e)}
            className="rounded-full glass px-3 py-1.5 text-xs transition hover:border-gold/40 hover:bg-gold/5"
          >
            {b.label}
          </button>
        ))}
      </div>
    </div>
  );
}
