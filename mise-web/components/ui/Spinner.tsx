/**
 * Spinner — lightweight loading indicator.
 * Usage: show while data is loading (isLoading from SWR hooks).
 */

import { clsx } from "clsx";

interface SpinnerProps {
    /** Size variant; defaults to "md" */
    size?: "sm" | "md" | "lg";
    className?: string;
}

const sizeClasses: Record<NonNullable<SpinnerProps["size"]>, string> = {
    sm: "h-4 w-4",
    md: "h-6 w-6",
    lg: "h-10 w-10",
};

/**
 * @example
 * {isLoading && <Spinner />}
 * <Spinner size="lg" className="text-mise-amber" />
 */
export function Spinner({ size = "md", className }: SpinnerProps) {
    return (
        <svg
            className={clsx("animate-spin text-mise-amber", sizeClasses[size], className)}
            viewBox="0 0 24 24"
            fill="none"
            aria-label="Loading"
            role="status"
        >
            <circle
                className="opacity-25"
                cx="12" cy="12" r="10"
                stroke="currentColor"
                strokeWidth="4"
            />
            <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
            />
        </svg>
    );
}
