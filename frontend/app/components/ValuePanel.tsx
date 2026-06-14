"use client";

export type ValueAnalysis = {
  outcomes: {
    outcome: string;
    decimal_odds: number;
    model_prob: number;
    market_prob: number;
    edge: number;
    fair_odds: number | null;
    kelly_stake_pct: number;
  }[];
  overround_pct: number;
  best_value: { outcome: string; edge: number } | null;
  verdict: string;
  source: string;
};

export function ValuePanel({ data }: { data: ValueAnalysis }) {
  return (
    <div className="glass rounded-3xl p-6">
      <div className="mb-1 flex items-center justify-between">
        <h3 className="font-semibold">💎 מנוע ערך מול השוק</h3>
        <span className="text-xs text-white/40">מרווח בוקמייקר {data.overround_pct}%</span>
      </div>
      <p className="mb-5 text-sm text-gold">{data.verdict}</p>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-white/50">
              <th className="py-2 text-right">תוצאה</th>
              <th className="py-2">יחס</th>
              <th className="py-2">מודל</th>
              <th className="py-2">שוק</th>
              <th className="py-2">Edge</th>
              <th className="py-2">Kelly</th>
            </tr>
          </thead>
          <tbody>
            {data.outcomes.map((o) => {
              const valuePlus = o.edge > 0;
              return (
                <tr key={o.outcome} className={`border-t border-white/5 ${valuePlus ? "bg-emerald-400/5" : ""}`}>
                  <td className="py-2.5 text-right font-medium">{o.outcome}</td>
                  <td className="py-2.5 text-center">{o.decimal_odds}</td>
                  <td className="py-2.5 text-center text-white/70">{o.model_prob}%</td>
                  <td className="py-2.5 text-center text-white/70">{o.market_prob}%</td>
                  <td className={`py-2.5 text-center font-semibold ${valuePlus ? "text-emerald-400" : "text-red-400/80"}`}>
                    {valuePlus ? "+" : ""}
                    {o.edge}%
                  </td>
                  <td className="py-2.5 text-center text-gold">{o.kelly_stake_pct > 0 ? `${o.kelly_stake_pct}%` : "—"}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      <p className="mt-3 text-xs text-white/40">
        Edge חיובי = המודל מעריך סיכוי גבוה מהמשתמע מהיחס. Kelly = גודל הימור מומלץ (¼ Kelly). לא ייעוץ פיננסי.
      </p>
    </div>
  );
}
