import * as React from "react";
import { cn } from "../../utils/cn";

export function Card({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("bg-neo-white neo-border neo-shadow p-6", className)} {...props} />;
}
