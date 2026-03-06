/**
 * Input primitive — text input field with an optional label and error message.
 */

import { type InputHTMLAttributes, forwardRef } from "react";
import { clsx } from "clsx";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
    label?: string;
    error?: string;
}

/**
 * @example
 * <Input label="Item name" placeholder="e.g. Margherita" value={…} onChange={…} />
 * <Input label="Price" type="number" error="Price must be positive" />
 */
export const Input = forwardRef<HTMLInputElement, InputProps>(function Input(
    { label, error, id, className, ...props },
    ref,
) {
    const inputId = id ?? label?.toLowerCase().replace(/\s+/g, "-");

    return (
        <div className="flex flex-col gap-1">
            {label && (
                <label htmlFor={inputId} className="mise-label">
                    {label}
                </label>
            )}
            <input
                id={inputId}
                ref={ref}
                className={clsx(
                    "mise-input",
                    error && "border-red-500 focus:ring-red-500",
                    className,
                )}
                {...props}
            />
            {error && <p className="text-xs text-red-400 mt-0.5">{error}</p>}
        </div>
    );
});
