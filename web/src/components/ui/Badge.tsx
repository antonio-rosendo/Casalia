import * as React from "react";
import { cn } from "../../utils/cn";

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "warning" | "destructive" | "outline";
}

export function Badge({ className, variant = "default", ...props }: BadgeProps) {
  return (
    <div
      className={cn(
        "inline-flex items-center px-2.5 py-0.5 text-xs font-bold tracking-tight border-2 border-neo-black uppercase",
        variant === "default" && "bg-neo-black text-neo-white",
        variant === "warning" && "bg-neo-yellow text-neo-black",
        variant === "destructive" && "bg-neo-orange text-neo-white",
        variant === "outline" && "bg-neo-white text-neo-black",
        className
      )}
      {...props}
    />
  );
}