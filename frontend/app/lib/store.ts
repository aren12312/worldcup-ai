import { create } from "zustand";

export type SimParams = {
  team1_xg: number;
  team2_xg: number;
  rho: number;
  team1: string;
  team2: string;
};

type OutPlayer = { name: string; team: 1 | 2; impact: number };

type SimState = {
  base: SimParams | null;
  out: Record<string, OutPlayer>;
  setBase: (p: SimParams) => void;
  togglePlayer: (key: string, player: OutPlayer) => void;
  reset: () => void;
  adjustedXg: () => { t1: number; t2: number };
};

// A removed player drops their team's xG proportionally to their impact rating.
const MAX_PLAYER_EFFECT = 0.0045; // per impact point; impact 90 => ~0.40 xG swing cap via dampening

function teamReduction(players: OutPlayer[]): number {
  // Diminishing returns when several players are out.
  let factor = 1;
  for (const p of players.sort((a, b) => b.impact - a.impact)) {
    factor -= p.impact * MAX_PLAYER_EFFECT * factor * 0.9;
  }
  return Math.max(0.45, factor);
}

export const useSimStore = create<SimState>((set, get) => ({
  base: null,
  out: {},
  setBase: (p) => set({ base: p, out: {} }),
  togglePlayer: (key, player) =>
    set((s) => {
      const out = { ...s.out };
      if (out[key]) delete out[key];
      else out[key] = player;
      return { out };
    }),
  reset: () => set({ out: {} }),
  adjustedXg: () => {
    const { base, out } = get();
    if (!base) return { t1: 0, t2: 0 };
    const t1Out = Object.values(out).filter((p) => p.team === 1);
    const t2Out = Object.values(out).filter((p) => p.team === 2);
    return {
      t1: Math.max(0.2, base.team1_xg * teamReduction(t1Out)),
      t2: Math.max(0.2, base.team2_xg * teamReduction(t2Out)),
    };
  },
}));
