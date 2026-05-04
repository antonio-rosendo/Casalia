import * as React from "react";
import { cn } from "../../utils/cn";

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline" | "ghost";
  size?: "sm" | "md" | "lg";
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", size = "md", ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={cn(
          "inline-flex items-center justify-center font-bold tracking-tight transition-all duration-200 cursor-pointer active:scale-95 disabled:pointer-events-none disabled:opacity-50",
          "neo-border",
          variant === "primary" &&
            "bg-neo-yellow text-neo-black neo-shadow neo-shadow-hover",
          variant === "secondary" &&
            "bg-neo-black text-neo-white neo-shadow-heavy shadow-neo-orange hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-neo",
          variant === "outline" &&
            "bg-neo-white text-neo-black neo-shadow neo-shadow-hover hover:bg-neo-gray",
          variant === "ghost" &&
            "border-transparent bg-transparent hover:bg-neo-gray hover:border-neo-black",
          size === "sm" && "h-9 px-4 text-sm",
          size === "md" && "h-12 px-6 text-base",
          size === "lg" && "h-14 px-8 text-lg",
          className
        )}
        {...props}
      />
    );
  }
);
Button.displayName = "Button";