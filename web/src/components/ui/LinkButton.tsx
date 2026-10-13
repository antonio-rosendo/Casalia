import * as React from "react";
import { cn } from "../../utils/cn";

interface LinkButtonProps extends React.AnchorHTMLAttributes<HTMLAnchorElement> {
  variant?: "primary" | "secondary";
  external?: boolean;
}

export function LinkButton({ variant = "primary", external, className, ...props }: LinkButtonProps) {
  return (
    <a
      {...(external && { target: "_blank", rel: "noreferrer" })}
      className={cn(
        "inline-flex items-center justify-center gap-2 h-12 px-8 w-full sm:w-auto whitespace-nowrap",
        "font-mono font-bold uppercase text-base border-2 border-neo-black neo-shadow neo-shadow-hover",
        "transition-colors active:translate-y-0.5 active:shadow-none",
        variant === "primary" && "bg-neo-black text-neo-white hover:bg-neo-orange",
        variant === "secondary" && "bg-neo-white text-neo-black hover:bg-neo-yellow hover:text-ink",
        className,
      )}
      {...props}
    />
  );
}
