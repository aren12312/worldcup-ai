"use client";

import { useEffect, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";

type Props = {
  value: string;
  onChange: (v: string) => void;
  placeholder: string;
  label: string;
};

export function TeamAutocomplete({ value, onChange, placeholder, label }: Props) {
  const [teams, setTeams] = useState<string[]>([]);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    fetch(`${API_URL}/teams?lang=he`)
      .then((r) => r.json())
      .then((d) => setTeams(d.teams || []))
      .catch(() => {});
  }, []);

  const filtered = teams.filter(
    (t) => t.includes(value) || value === "" || t.toLowerCase().includes(value.toLowerCase())
  ).slice(0, 8);

  return (
    <div className="relative">
      <span className="mb-2 block text-sm text-white/50">{label}</span>
      <input
        value={value}
        onChange={(e) => { onChange(e.target.value); setOpen(true); }}
        onFocus={() => setOpen(true)}
        onBlur={() => setTimeout(() => setOpen(false), 150)}
        className="w-full rounded-2xl border border-white/10 bg-pitch-950 px-4 py-3.5 text-right outline-none transition focus:border-gold/50 focus:ring-2 focus:ring-gold/20"
        placeholder={placeholder}
      />
      {open && filtered.length > 0 && value.length > 0 && (
        <ul className="absolute z-20 mt-1 max-h-48 w-full overflow-auto rounded-xl border border-white/10 bg-pitch-900 shadow-xl">
          {filtered.map((t) => (
            <li key={t}>
              <button
                type="button"
                className="w-full px-4 py-2.5 text-right text-sm hover:bg-gold/10"
                onMouseDown={() => { onChange(t); setOpen(false); }}
              >
                {t}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
