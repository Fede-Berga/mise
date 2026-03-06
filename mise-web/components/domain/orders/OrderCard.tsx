/**
 * OrderCard — displays a single order on the Kanban board.
 * Shows total, item count, table label, and time since placement.
 */

import { Card } from "@/components/ui/Card";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { Button } from "@/components/ui/Button";
import { formatCurrency } from "@/lib/utils/currency";
import { formatRelative } from "@/lib/utils/date";
import type { Order, OrderStatus } from "@/lib/types/orders";
import { ORDER_STATUS_LABELS } from "@/lib/types/orders";
import { ArrowRight, Table2 } from "lucide-react";

/** Next valid status in the order lifecycle */
const NEXT_STATUS: Partial<Record<OrderStatus, OrderStatus>> = {
    NEW: "IN_PREPARATION",
    IN_PREPARATION: "READY",
    READY: "CLOSED",
};

interface OrderCardProps {
    order: Order;
    onAdvance: (order: Order, nextStatus: OrderStatus) => Promise<void>;
    advancing?: boolean;
}

/**
 * @example
 * <OrderCard order={order} onAdvance={handleAdvance} />
 */
export function OrderCard({ order, onAdvance, advancing }: OrderCardProps) {
    const nextStatus = NEXT_STATUS[order.status as OrderStatus];

    return (
        <Card className="flex flex-col gap-3">
            {/* Top row: order ID + status */}
            <div className="flex items-center justify-between">
                <span className="text-xs font-mono text-mise-text-muted">#{order.id}</span>
                <StatusBadge status={order.status as OrderStatus} />
            </div>

            {/* Table label */}
            {order.table_id && (
                <div className="flex items-center gap-1.5 text-xs text-mise-text-muted">
                    <Table2 size={12} />
                    <span>Table {order.table_id}</span>
                </div>
            )}

            {/* Items summary */}
            <p className="text-xs text-mise-text-muted">
                {order.items.length} {order.items.length === 1 ? "item" : "items"}
            </p>

            {/* Notes */}
            {order.notes && (
                <p className="text-xs italic text-mise-text-muted line-clamp-2 border-l-2 border-mise-amber pl-2">
                    {order.notes}
                </p>
            )}

            {/* Footer: total + time + action */}
            <div className="flex items-center justify-between mt-auto pt-2 border-t border-mise-border">
                <div>
                    <p className="text-sm font-bold text-mise-text">{formatCurrency(order.total_amount)}</p>
                    <p className="text-[10px] text-mise-text-faint">{formatRelative(order.created_at)}</p>
                </div>

                {nextStatus && (
                    <Button
                        size="sm"
                        variant="secondary"
                        loading={advancing}
                        onClick={() => onAdvance(order, nextStatus)}
                        className="text-xs gap-1.5"
                    >
                        {ORDER_STATUS_LABELS[nextStatus]}
                        <ArrowRight size={12} />
                    </Button>
                )}
            </div>
        </Card>
    );
}
