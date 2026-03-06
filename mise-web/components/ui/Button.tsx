/**
 * Button primitive.
 *
 * Variants:
 *   primary  — amber CTA button (main actions)
 *   secondary — ghost/outline (secondary actions)
 *   danger   — destructive action
 *   ghost    — no background (toolbar / icon buttons)
 *
 * Extending: add a new key to `variants` and `sizes` as needed.
 */

import { type ButtonHTMLAttributes } from "react";
import { clsx } from "clsx";

type Variant = "primary" | "secondary" | "danger" | "ghost";
type Size = "sm" | "md" | "lg";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: Variant;
    size?: Size;
    loading?: boolean;
}

const variants: Record<Variant, string> = {
    primary:
        "bg-mise-amber text-neutral-950 hover:bg-mise-amber-light active:bg-mise-amber-dark font-semibold shadow-sm",
    secondary:
        "border border-mise-border text-mise-text hover:bg-mise-raised active:bg-neutral-700",
    danger:
        "bg-red-600 text-white hover:bg-red-500 active:bg-red-700 font-semibold",
    ghost:
        "text-mise-text-muted hover:text-mise-text hover:bg-mise-raised",
};

const sizes: Record<Size, string> = {
    sm: "px-3 py-1.5 text-xs rounded-lg",
    md: "px-4 py-2   text-sm rounded-xl",
    lg: "px-6 py-3   text-base rounded-xl",
};

/**
 * @example
 * <Button variant="primary" onClick={...}>Save</Button>
 * <Button variant="secondary" size="sm">Cancel</Button>
 * <Button variant="danger" loading>Deleting…</Button>
 */
export function Button({
    variant = "secondary",
    size = "md",
    loading = false,
    disabled,
    children,
    className,
    ...props
}: ButtonProps) {
    return (
        <button
            disabled={disabled || loading}
            className={clsx(
                // Base styles
                "inline-flex items-center justify-center gap-2",
                "transition-colors duration-150 focus-visible:outline-none",
                "focus-visible:ring-2 focus-visible:ring-mise-amber focus-visible:ring-offset-2",
                "focus-visible:ring-offset-mise-bg disabled:opacity-40 disabled:cursor-not-allowed",
                variants[variant],
                sizes[size],
                className,
            )}
            {...props}
        >
            {loading && (
                <svg
                    className="animate-spin h-4 w-4 shrink-0"
                    viewBox="0 0 24 24"
                    fill="none"
                    aria-hidden
                >
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                </svg>
            )}
            {children}
        </button>
    );
}
