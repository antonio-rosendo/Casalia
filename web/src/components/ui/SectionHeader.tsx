import type { ReactNode } from "react";

export function SectionHeader({ title, children }: { title: string; children?: ReactNode }) {
  return (
    <div className="mb-10 max-w-3xl">
      <h2 className="text-4xl md:text-5xl font-bold uppercase tracking-tighter mb-4">{title}</h2>
      <div className="w-full h-1 bg-neo-black mb-6" />
      {children && <div className="text-lg text-neo-darkgray leading-relaxed">{children}</div>}
    </div>
  );
}
