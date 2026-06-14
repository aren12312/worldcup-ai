"use client";

import {
  Legend,
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ResponsiveContainer,
} from "recharts";

type Metric = { label: string; team1: number; team2: number };

export function TacticalRadar({
  metrics,
  team1,
  team2,
}: {
  metrics: Record<string, Metric>;
  team1: string;
  team2: string;
}) {
  const data = Object.values(metrics).map((m) => ({
    metric: m.label,
    [team1]: m.team1,
    [team2]: m.team2,
  }));

  return (
    <div className="glass rounded-3xl p-6">
      <h3 className="mb-2 font-semibold">🧬 DNA טקטי</h3>
      <p className="mb-4 text-xs text-white/50">פרופיל קבוצתי רב-ממדי</p>
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={data} outerRadius="72%">
            <PolarGrid stroke="#ffffff20" />
            <PolarAngleAxis dataKey="metric" tick={{ fill: "#ffffffcc", fontSize: 12 }} />
            <PolarRadiusAxis domain={[0, 100]} tick={{ fill: "#ffffff40", fontSize: 10 }} angle={90} />
            <Radar name={team1} dataKey={team1} stroke="#10b981" fill="#10b981" fillOpacity={0.35} />
            <Radar name={team2} dataKey={team2} stroke="#f5c542" fill="#f5c542" fillOpacity={0.3} />
            <Legend wrapperStyle={{ fontSize: 12 }} />
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
