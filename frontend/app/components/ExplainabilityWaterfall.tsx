"use client";

type Factor = { label: string; value: number };

export function ExplainabilityWaterfall({
  team,
  xg,
  factors,
}: {
  team: string;
  xg: number;
  factors: Factor[];
}) {
  const maxAbs = Math.max(...factors.map((f) => Math.abs(f.value)), 0.1);
  let running = 0;

  return (
    <div className="glass rounded-3xl p-6">
      <div className="mb-4 flex items-baseline justify-between">
        <h3 className="font-semibold">למה {xg} xG?</h3>
        <span className="text-sm text-white/50">{team}</span>
      </div>
      <p className="mb-4 text-xs text-white/50">פירוק תרומת כל גורם ל-xG הצפוי</p>

      <div className="space-y-3">
        {factors.map((f) => {
          const positive = f.value >= 0;
          const width = (Math.abs(f.value) / maxAbs) * 50;
          const left = positive ? 50 : 50 - width;
          running += f.value;
          return (
            <div key={f.label} className="flex items-center gap-3">
              <span className="w-24 shrink-0 text-xs text-white/70">{f.label}</span>
              <div className="relative h-7 flex-1 rounded-lg bg-black/30">
                <div className="absolute inset-y-0 left-1/2 w-px bg-white/20" />
                <div
                  className={`absolute inset-y-1 rounded-md ${
                    positive ? "bg-emerald-400/80" : "bg-red-400/80"
                  }`}
                  style={{ left: `${left}%`, width: `${width}%` }}
                />
              </div>
              <span className={`w-12 shrink-0 text-left text-xs font-semibold ${positive ? "text-emerald-400" : "text-red-400"}`}>
                {positive ? "+" : ""}
                {f.value}
              </span>
            </div>
          );
        })}
      </div>

      <div className="mt-4 flex items-center justify-between border-t border-white/10 pt-3">
        <span className="text-sm font-semibold">xG סופי</span>
        <span className="text-xl font-bold text-gold">{xg}</span>
      </div>
    </div>
  );
}
