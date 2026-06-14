// Client-side match simulation mirroring the backend Dixon-Coles engine.
// Cheap enough (max 9x9 grid) to run instantly on every interaction.

const MAX_GOALS = 8;
export const DEFAULT_RHO = -0.06;

function factorial(n: number): number {
  let r = 1;
  for (let i = 2; i <= n; i++) r *= i;
  return r;
}

function poissonPmf(k: number, lam: number): number {
  return (Math.pow(lam, k) * Math.exp(-lam)) / factorial(k);
}

function dixonColesTau(h: number, a: number, lam: number, mu: number, rho: number): number {
  if (h === 0 && a === 0) return 1 - lam * mu * rho;
  if (h === 0 && a === 1) return 1 + lam * rho;
  if (h === 1 && a === 0) return 1 + mu * rho;
  if (h === 1 && a === 1) return 1 - rho;
  return 1;
}

export function scoreMatrix(t1xg: number, t2xg: number, rho = DEFAULT_RHO, maxGoals = MAX_GOALS): number[][] {
  const home = Array.from({ length: maxGoals + 1 }, (_, i) => poissonPmf(i, t1xg));
  const away = Array.from({ length: maxGoals + 1 }, (_, j) => poissonPmf(j, t2xg));
  const matrix: number[][] = [];
  let total = 0;
  for (let h = 0; h <= maxGoals; h++) {
    matrix[h] = [];
    for (let a = 0; a <= maxGoals; a++) {
      let p = home[h] * away[a];
      if (h < 2 && a < 2) p *= dixonColesTau(h, a, t1xg, t2xg, rho);
      matrix[h][a] = p;
      total += p;
    }
  }
  if (total > 0) {
    for (let h = 0; h <= maxGoals; h++) for (let a = 0; a <= maxGoals; a++) matrix[h][a] /= total;
  }
  return matrix;
}

export type SimResult = {
  team1Win: number;
  draw: number;
  team2Win: number;
  over25: number;
  btts: number;
};

export function probabilities(t1xg: number, t2xg: number, rho = DEFAULT_RHO): SimResult {
  const m = scoreMatrix(t1xg, t2xg, rho);
  let t1 = 0,
    dr = 0,
    t2 = 0,
    over = 0,
    btts = 0;
  for (let h = 0; h < m.length; h++) {
    for (let a = 0; a < m.length; a++) {
      const p = m[h][a];
      if (h > a) t1 += p;
      else if (h < a) t2 += p;
      else dr += p;
      if (h + a > 2) over += p;
      if (h > 0 && a > 0) btts += p;
    }
  }
  const pct = (x: number) => Math.round(x * 1000) / 10;
  return { team1Win: pct(t1), draw: pct(dr), team2Win: pct(t2), over25: pct(over), btts: pct(btts) };
}

export function gridPercent(t1xg: number, t2xg: number, maxGoals = 5, rho = DEFAULT_RHO): number[][] {
  const m = scoreMatrix(t1xg, t2xg, rho, Math.max(maxGoals, MAX_GOALS));
  const grid: number[][] = [];
  for (let h = 0; h <= maxGoals; h++) {
    grid[h] = [];
    for (let a = 0; a <= maxGoals; a++) grid[h][a] = Math.round(m[h][a] * 1000) / 10;
  }
  return grid;
}

// Minute-by-minute win-probability trajectory driven by remaining xG.
export function momentumTimeline(
  t1xg: number,
  t2xg: number,
  events: { minute: number; team: 1 | 2; type: "goal" | "red" }[] = []
): { minute: number; team1: number; draw: number; team2: number }[] {
  const points: { minute: number; team1: number; draw: number; team2: number }[] = [];
  for (let minute = 0; minute <= 90; minute += 5) {
    const remaining = (90 - minute) / 90;
    let t1Goals = 0;
    let t2Goals = 0;
    let l1 = t1xg * remaining;
    let l2 = t2xg * remaining;
    for (const e of events) {
      if (e.minute <= minute) {
        if (e.type === "goal") e.team === 1 ? t1Goals++ : t2Goals++;
        if (e.type === "red") e.team === 1 ? (l1 *= 0.7) : (l2 *= 0.7);
      }
    }
    // Score-adjusted remaining: shift expected goals by current lead.
    const adjXg1 = Math.max(0.05, l1) + t1Goals;
    const adjXg2 = Math.max(0.05, l2) + t2Goals;
    const p = probabilities(adjXg1, adjXg2);
    points.push({ minute, team1: p.team1Win, draw: p.draw, team2: p.team2Win });
  }
  return points;
}
