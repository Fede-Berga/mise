/**
 * Card primitive — base surface container.
 *
 * Props:
 *   hover   — adds amber border on hover (for clickable cards)
 *   padding — default true; set false for flush content (e.g. tables)
 */

import { type HTMLAttributes } from "react";
import { clsx } from "clsx";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
    hover?: boolean;
    padding?: boolean;
}

/**
 * @example
 * <Card>…content…</Card>
 * <Card hover className="cursor-pointer" onClick={…}>…</Card>
 * <Card padding={false}><table>…</table></Card>
 */
export function Card({ hover = false, padding = true, children, className, ...props }: CardProps) {
    return (
        <div
            className={clsx(
                "mise-card",
                padding && "p-5",
                hover && "hover:border-mise-amber cursor-pointer",
                "animate-fade-in",
                className,
            )}
            {...props}
        >
            {children}
        </div>
    );
}
