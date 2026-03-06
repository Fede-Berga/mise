/**
 * MenuItemForm — create or edit a menu item.
 * Stateless controlled form; parent manages submission and loading state.
 */

"use client";

import { useState, useEffect } from "react";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import type { MenuItem, MenuItemCreate, MenuItemUpdate } from "@/lib/types/menu";
import { clsx } from "clsx";

// Predefined categories; extend this list as the menu grows
const CATEGORIES = ["Starters", "Mains", "Desserts", "Drinks", "Sides", "Specials", "Uncategorised"];

interface MenuItemFormProps {
    /** Existing item for edit mode; undefined = create mode */
    initialValues?: MenuItem;
    loading?: boolean;
    onSubmit: (data: MenuItemCreate | MenuItemUpdate) => Promise<void>;
    onCancel: () => void;
}

/**
 * @example
 * <MenuItemForm onSubmit={handleCreate} onCancel={closeModal} />
 * <MenuItemForm initialValues={item} onSubmit={handleUpdate} onCancel={closeModal} />
 */
export function MenuItemForm({ initialValues, loading, onSubmit, onCancel }: MenuItemFormProps) {
    const [name, setName] = useState(initialValues?.name ?? "");
    const [description, setDescription] = useState(initialValues?.description ?? "");
    const [price, setPrice] = useState(String(initialValues?.price ?? ""));
    const [category, setCategory] = useState(initialValues?.category ?? "Uncategorised");
    const [isAvailable, setIsAvailable] = useState(initialValues?.is_available ?? true);
    const [errors, setErrors] = useState<Record<string, string>>({});

    // Reset form when initialValues change (e.g., switching between items to edit)
    useEffect(() => {
        setName(initialValues?.name ?? "");
        setDescription(initialValues?.description ?? "");
        setPrice(String(initialValues?.price ?? ""));
        setCategory(initialValues?.category ?? "Uncategorised");
        setIsAvailable(initialValues?.is_available ?? true);
        setErrors({});
    }, [initialValues?.id]);

    function validate(): boolean {
        const errs: Record<string, string> = {};
        if (!name.trim()) errs.name = "Name is required";
        const p = parseFloat(price);
        if (isNaN(p) || p <= 0) errs.price = "Price must be a positive number";
        setErrors(errs);
        return Object.keys(errs).length === 0;
    }

    async function handleSubmit(e: React.FormEvent) {
        e.preventDefault();
        if (!validate()) return;
        await onSubmit({
            name: name.trim(),
            description: description.trim() || null,
            price: parseFloat(price),
            category,
            is_available: isAvailable,
        });
    }

    return (
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <Input label="Item name" value={name} onChange={(e) => setName(e.target.value)} error={errors.name} placeholder="e.g. Truffle Risotto" required />
            <Input label="Description" value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Optional description" />
            <div className="grid grid-cols-2 gap-3">
                <Input label="Price (€)" type="number" step="0.01" min="0" value={price} onChange={(e) => setPrice(e.target.value)} error={errors.price} placeholder="0.00" required />
                <div className="flex flex-col gap-1">
                    <label className="mise-label">Category</label>
                    <select value={category} onChange={(e) => setCategory(e.target.value)} className="mise-input">
                        {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
                    </select>
                </div>
            </div>

            {/* Available toggle */}
            <label className="flex items-center gap-3 cursor-pointer select-none">
                <button
                    type="button"
                    role="switch"
                    aria-checked={isAvailable}
                    onClick={() => setIsAvailable((v) => !v)}
                    className={clsx(
                        "relative h-5 w-9 rounded-full transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-mise-amber",
                        isAvailable ? "bg-mise-amber" : "bg-neutral-700",
                    )}
                >
                    <span className={clsx("absolute top-0.5 left-0.5 h-4 w-4 rounded-full bg-white shadow-sm transition-transform duration-200", isAvailable && "translate-x-4")} />
                </button>
                <span className="text-sm text-mise-text">Available for ordering</span>
            </label>

            <div className="flex justify-end gap-2 pt-2 border-t border-mise-border">
                <Button type="button" variant="ghost" onClick={onCancel} disabled={loading}>Cancel</Button>
                <Button type="submit" variant="primary" loading={loading}>
                    {initialValues ? "Save changes" : "Add item"}
                </Button>
            </div>
        </form>
    );
}
