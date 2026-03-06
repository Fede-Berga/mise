/**
 * TicketCard — kitchen display system (KDS) card.
 *
 * Shows ticket items, table label, elapsed time, and an advance-status button.
 * Cards for NEW tickets pulse amber to draw attention.
 */

"use client";

import { Card } from "@/components/ui/Card";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { Button } from "@/components/ui/Button";
import { formatRelative } from "@/lib/utils/date";
import type { KitchenTicket, TicketStatus } from "@/lib/types/kitchen";
import { TICKET_NEXT_STATUS, TICKET_STATUS_LABELS } from "@/lib/types/kitchen";
import { clsx } from "clsx";
import { Clock, Table2, ArrowRight } from "lucide-react";

interface TicketCardProps {
    ticket: KitchenTicket;
    onAdvance: (ticket: KitchenTicket, nextStatus: TicketStatus) => Promise<void>;
    advancing?: boolean;
}

/**
 * @example
 * <TicketCard ticket={ticket} onAdvance={handleAdvance} />
 */
export function TicketCard({ ticket, onAdvance, advancing }: TicketCardProps) {
    const nextStatus = TICKET_NEXT_STATUS[ticket.status as TicketStatus];
    const isNew = ticket.status === "NEW";
    const isDone = ticket.status === "DONE";

    return (
        <Card
            className={clsx(
                "flex flex-col gap-3 relative",
                isNew && "animate-pulse-amber border-amber-500/40",
                isDone && "opacity-60",
            )}
        >
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <span className="text-xs font-mono text-mise-text-muted">#{ticket.id}</span>
                    {ticket.table_label && (
                        <span className="flex items-center gap-1 text-xs text-mise-text-muted">
                            <Table2 size={11} />
                            {ticket.table_label}
                        </span>
                    )}
                </div>
                <StatusBadge status={ticket.status as TicketStatus} />
            </div>

            {/* Item list */}
            <ul className="flex flex-col gap-1.5">
                {ticket.items.map((item) => (
                    <li key={item.id} className="flex items-start gap-2 text-sm">
                        <span className="font-bold text-mise-amber tabular-nums w-5 shrink-0">{item.quantity}×</span>
                        <div className="flex-1 min-w-0">
                            <p className="text-mise-text">{item.menu_item_name}</p>
                            {item.notes && (
                                <p className="text-xs text-amber-400 italic mt-0.5">{item.notes}</p>
                            )}
                        </div>
                    </li>
                ))}
            </ul>

            {/* Footer */}
            <div className="flex items-center justify-between pt-2 border-t border-mise-border">
                <div className="flex items-center gap-1.5 text-xs text-mise-text-faint">
                    <Clock size={11} />
                    <span>{formatRelative(ticket.created_at)}</span>
                </div>

                {nextStatus && !isDone && (
                    <Button
                        size="sm"
                        variant={isNew ? "primary" : "secondary"}
                        loading={advancing}
                        onClick={() => onAdvance(ticket, nextStatus)}
                        className="text-xs gap-1.5"
                    >
                        {TICKET_STATUS_LABELS[nextStatus]}
                        <ArrowRight size={12} />
                    </Button>
                )}
            </div>
        </Card>
    );
}
