/**
 * RestaurantSwitcher — dropdown for owners to switch between their properties.
 * Only rendered when the user has the "owner" role and multiple restaurants.
 */

"use client";

import { useState, useRef, useEffect } from "react";
import { ChevronDown, Store } from "lucide-react";
import { useSession } from "next-auth/react";
import { clsx } from "clsx";

interface Props {
    /** Called after a successful restaurant switch */
    onSwitch?: (restaurantId: string) => void;
}

export function RestaurantSwitcher({ onSwitch }: Props) {
    const { data: session } = useSession();
    const [open, setOpen] = useState(false);
    const [active, setActive] = useState(session?.user?.activeRestaurantId ?? "");
    const ref = useRef<HTMLDivElement>(null);

    const restaurantIds = session?.user?.restaurantIds ?? [];

    const handleSwitch = async (id: string) => {
        setOpen(false);
        const res = await fetch("/api/auth/switch-restaurant", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ restaurantId: id }),
        });
        if (res.ok) { setActive(id); onSwitch?.(id); }
    };

    // Keep local active id aligned with session updates from NextAuth.
    useEffect(() => {
        setActive(session?.user?.activeRestaurantId ?? "");
    }, [session?.user?.activeRestaurantId]);

    // Close on outside click
    useEffect(() => {
        const handler = (e: MouseEvent) => {
            if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
        };
        document.addEventListener("mousedown", handler);
        return () => document.removeEventListener("mousedown", handler);
    }, []);

    if (session?.user?.role !== "owner" || restaurantIds.length < 2) return null;

    const displayName = (id: string) => id.replace("restaurant-", "Location ");

    return (
        <div ref={ref} className="relative">
            <button
                onClick={() => setOpen((o) => !o)}
                className="flex items-center gap-2 rounded-lg border border-mise-border bg-mise-surface px-3 py-1.5 text-sm text-mise-text hover:bg-mise-raised transition-colors"
            >
                <Store size={14} className="text-mise-amber shrink-0" />
                <span className="max-w-[140px] truncate">{displayName(active || restaurantIds[0])}</span>
                <ChevronDown size={13} className={clsx("shrink-0 transition-transform", open && "rotate-180")} />
            </button>

            {open && (
                <div className="absolute top-full left-0 mt-1 z-50 min-w-[180px] rounded-xl border border-mise-border bg-mise-surface shadow-xl overflow-hidden">
                    {restaurantIds.map((id) => (
                        <button
                            key={id}
                            onClick={() => handleSwitch(id)}
                            className={clsx(
                                "flex w-full items-center gap-2 px-4 py-2.5 text-sm text-left transition-colors",
                                id === (active || restaurantIds[0])
                                    ? "bg-mise-amber/10 text-mise-amber font-medium"
                                    : "text-mise-text hover:bg-mise-raised"
                            )}
                        >
                            <Store size={13} className="shrink-0" />
                            {displayName(id)}
                        </button>
                    ))}
                </div>
            )}
        </div>
    );
}
