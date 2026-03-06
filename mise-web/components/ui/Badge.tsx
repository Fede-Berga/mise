/**
 * Badge — small pill label for status or category display.
 *
 * Variants match semantic intent, not specific domain entities, so they
 * can be reused across menu, orders, and kitchen.
 */

import { clsx } from "clsx";
import { type HTMLAttributes } from "react";

type BadgeVariant = "default" | "amber" | "green" | "red" | "indigo" | "zinc";

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
    variant?: BadgeVariant;
}

const variants: Record<BadgeVariant, string> = {
    default: "bg-neutral-800 text-neutral-300 border-neutral-700",
    amber: "bg-amber-500/15  text-amber-400  border-amber-500/30",
    green: "bg-green-500/15  text-green-400  border-green-500/30",
    red: "bg-red-500/15    text-red-400    border-red-500/30",
    indigo: "bg-indigo-500/15 text-indigo-400 border-indigo-500/30",
    zinc: "bg-zinc-800      text-zinc-400   border-zinc-700",
};

/**
 * @example
 * <Badge variant="green">Available</Badge>
 * <Badge variant="amber">In Preparation</Badge>
 */
export function Badge({ variant = "default", children, className, ...props }: BadgeProps) {
    return (
        <span
            className={clsx(
                "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium",
                variants[variant],
                className,
            )}
            {...props}
        >
            {children}
        </span>
    );
}
