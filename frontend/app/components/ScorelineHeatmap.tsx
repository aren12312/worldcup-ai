"use client";

import { useMemo, useState } from "react";

function color(p: number, max: number): string {
  const intensity = max > 0 ? p / max : 0;
  // emerald -> gold gradient by intensity
  const r = Math.round(16 + intensity * (245 - 16));
  const g = Math.round(185 + intensity * (197 - 185));
  const b = Math.round(129 + intensity * (66 - 129));
  return `rgba(${r}, ${g}, ${b}, ${0.12 + intensity * 0.88})`;
}

export function ScorelineHeatmap({
  grid,
  team1,
  team2,
}: {
  grid: number[][];
  team1: string;
  team2: string;
}) {
  const [hover, setHover] = useState<{ h: number; a: number } | null>(null);
  const max = useMemo(() => Math.max(...grid.flat(), 0.01), [grid]);
  const best = useMemo(() => {
    let bh = 0,
      ba = 0,
      bp = -1;
    grid.forEach((row, h) =>
      row.forEach((p, a) => {
        if (p > bp) {
          bp = p;
          bh = h;
          ba = a;
        }
      })
    );
    return { h: bh, a: ba, p: bp };
  }, [grid]);

  return (
    <div className="glass rounded-3xl p-6">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="font-semibold">מפת חום — כל התוצאות</h3>
        <span className="text-xs text-white/50">
          סביר ביותר: <span className="text-gold">{best.h}-{best.a}</span> ({best.p}%)
        </span>
      </div>

      <div className="flex">
        <div className="flex flex-col justify-center pl-2 text-center">
          <span className="mb-2 origin-center -rotate-90 whitespace-nowrap text-xs text-white/50">
            {team1} ⚽
          </span>
        </div>
        <div className="flex-1">
          <div className="grid" style={{ gridTemplateColumns: `repeat(${grid[0].length}, minmax(0, 1fr))` }}>
            {grid.map((row, h) =>
              row.map((p, a) => {
                const isBest = h === best.h && a === best.a;
                const isHover = hover?.h === h && hover?.a === a;
                return (
                  <div
                    key={`${h}-${a}`}
                    onMouseEnter={() => setHover({ h, a })}
                    onMouseLeave={() => setHover(null)}
                    className={`relative aspect-square cursor-default rounded-md border text-center transition ${
                      isBest ? "border-gold" : "border-transparent"
                    } ${isHover ? "scale-105 ring-1 ring-white/40" : ""}`}
                    style={{ background: color(p, max) }}
                  >
                    <span className="absolute inset-0 flex items-center justify-center text-[10px] font-semibold text-black/80 sm:text-xs">
                      {p >= 1 ? p : ""}
                    </span>
                  </div>
                );
              })
            )}
          </div>
          <div className="mt-1 grid text-center text-[10px] text-white/40" style={{ gridTemplateColumns: `repeat(${grid[0].length}, minmax(0, 1fr))` }}>
            {grid[0].map((_, a) => (
              <span key={a}>{a}</span>
            ))}
          </div>
          <p className="mt-2 text-center text-xs text-white/50">{team2} ⚽ (שערים)</p>
        </div>
      </div>

      {hover && (
        <p className="mt-3 text-center text-sm">
          <span className="text-white/60">
            {team1} {hover.h} - {hover.a} {team2}:
          </span>{" "}
          <span className="font-bold text-gold">{grid[hover.h][hover.a]}%</span>
        </p>
      )}
    </div>
  );
}
