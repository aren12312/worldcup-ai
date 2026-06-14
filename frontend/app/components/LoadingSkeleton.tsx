"use client";

export function LoadingSkeleton() {
  return (
    <div className="space-y-6">
      <div className="skeleton h-44 rounded-3xl" />
      <div className="flex gap-2">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="skeleton h-9 w-24 rounded-full" />
        ))}
      </div>
      <div className="grid gap-6 lg:grid-cols-2">
        <div className="skeleton h-72 rounded-3xl" />
        <div className="skeleton h-72 rounded-3xl" />
        <div className="skeleton h-64 rounded-3xl lg:col-span-2" />
      </div>
    </div>
  );
}
