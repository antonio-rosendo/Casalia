import * as React from "react";
import { cn } from "../../utils/cn";

export function Badge({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "inline-flex items-center px-2.5 py-0.5 text-xs font-bold tracking-tight border-2 border-neo-black uppercase bg-neo-yellow text-ink",
        className,
      )}
      {...props}
    />
  );
}
