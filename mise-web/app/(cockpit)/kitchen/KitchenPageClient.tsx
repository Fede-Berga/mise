/**
 * KitchenPageClient — Kitchen Display System (KDS).
 *
 * Shows all open tickets (NEW, PREPARING, READY) in a responsive grid.
 * Polls every 10 seconds via useKitchenTickets.
 * "Done" tickets are hidden by default, toggle to see them.
 *
 * Layout:
 *   Status filter tabs → filtered ticket grid
 *
 * Extending: add a priority field to the ticket to enable sorting by urgency.
 */

"use client";

import { useState } from "react";
import { useKitchenTickets } from "@/hooks/useKitchenTickets";
import { advanceTicketStatus } from "@/lib/api/kitchen";
import { TicketCard } from "@/components/domain/kitchen/TicketCard";
import { Spinner } from "@/components/ui/Spinner";
import type { KitchenTicket, TicketStatus } from "@/lib/types/kitchen";
import { TICKET_STATUS_LABELS } from "@/lib/types/kitchen";
import { clsx } from "clsx";
import { RefreshCw } from "lucide-react";

const FILTER_OPTIONS: Array<TicketStatus | "ALL"> = ["ALL", "NEW", "PREPARING", "READY", "DONE"];

const FILTER_COLORS: Record<TicketStatus, string> = {
    NEW: "text-indigo-400 border-indigo-500",
    PREPARING: "text-amber-400 border-amber-500",
    READY: "text-green-400 border-green-500",
    DONE: "text-zinc-500 border-zinc-600",
};

export function KitchenPageClient() {
    const { tickets, isLoading, error, mutate } = useKitchenTickets();
    const [activeFilter, setActiveFilter] = useState<TicketStatus | "ALL">("ALL");
    const [advancing, setAdvancing] = useState<number | null>(null);

    async function handleAdvance(ticket: KitchenTicket, nextStatus: TicketStatus) {
        setAdvancing(ticket.id);
        try {
            await advanceTicketStatus(ticket.id, nextStatus);
            await mutate();
        } finally {
            setAdvancing(null);
        }
    }

    const displayed = tickets.filter(
        (t) => activeFilter === "ALL" || t.status === activeFilter,
    );

    // Count per status for tab badges
    const countByStatus = tickets.reduce<Record<string, number>>((acc, t) => {
        acc[t.status] = (acc[t.status] ?? 0) + 1;
        return acc;
    }, {});

    return (
        <div className="flex flex-col gap-5">
            {/* Toolbar */}
            <div className="flex flex-wrap items-center gap-2">
                {/* Status filter tabs */}
                {FILTER_OPTIONS.map((f) => {
                    const count = f === "ALL" ? tickets.length : (countByStatus[f] ?? 0);
                    const isActive = activeFilter === f;
                    return (
                        <button
                            key={f}
                            onClick={() => setActiveFilter(f)}
                            className={clsx(
                                "flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors",
                                isActive
                                    ? f === "ALL"
                                        ? "bg-mise-amber text-neutral-950 border-mise-amber"
                                        : clsx("bg-mise-raised border", FILTER_COLORS[f as TicketStatus])
                                    : "border-mise-border text-mise-text-muted hover:text-mise-text hover:bg-mise-raised",
                            )}
                        >
                            {f === "ALL" ? "All" : TICKET_STATUS_LABELS[f as TicketStatus]}
                            <span className={clsx("rounded-full px-1.5 py-0.5 text-[10px] font-bold", isActive ? "bg-black/20" : "bg-mise-raised")}>
                                {count}
                            </span>
                        </button>
                    );
                })}

                {/* Manual refresh */}
                <button
                    onClick={() => mutate()}
                    aria-label="Refresh tickets"
                    className="ml-auto p-2 rounded-lg text-mise-text-muted hover:text-mise-text hover:bg-mise-raised transition-colors"
                >
                    <RefreshCw size={15} className={isLoading ? "animate-spin" : ""} />
                </button>
            </div>

            {/* Loading */}
            {isLoading && tickets.length === 0 && (
                <div className="flex justify-center py-24">
                    <Spinner size="lg" />
                </div>
            )}

            {/* Error */}
            {error && (
                <p className="text-sm text-red-400 text-center py-16">
                    Failed to load tickets. Is the kitchen-service running?
                </p>
            )}

            {/* Empty state */}
            {!isLoading && displayed.length === 0 && !error && (
                <div className="flex flex-col items-center py-24 text-center gap-3">
                    <span className="text-4xl">👨‍🍳</span>
                    <p className="text-sm text-mise-text-muted">
                        {activeFilter === "ALL" ? "No open tickets — service is running smoothly." : `No ${TICKET_STATUS_LABELS[activeFilter as TicketStatus].toLowerCase()} tickets.`}
                    </p>
                </div>
            )}

            {/* Ticket grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 gap-4">
                {displayed.map((ticket) => (
                    <TicketCard
                        key={ticket.id}
                        ticket={ticket}
                        onAdvance={handleAdvance}
                        advancing={advancing === ticket.id}
                    />
                ))}
            </div>
        </div>
    );
}
