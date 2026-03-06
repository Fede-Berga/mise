/**
 * StatusBadge — semantic badge for order/ticket statuses.
 *
 * Maps domain status strings to the correct Badge variant and label.
 * Keeps status → colour logic in one place.
 */

import { Badge } from "./Badge";
import type { OrderStatus } from "@/lib/types/orders";
import type { TicketStatus } from "@/lib/types/kitchen";
import { ORDER_STATUS_LABELS } from "@/lib/types/orders";
import { TICKET_STATUS_LABELS } from "@/lib/types/kitchen";

type AnyStatus = OrderStatus | TicketStatus;

const STATUS_VARIANT: Record<AnyStatus, "indigo" | "amber" | "green" | "zinc"> = {
    NEW: "indigo",
    IN_PREPARATION: "amber",
    PREPARING: "amber",
    READY: "green",
    CLOSED: "zinc",
    DONE: "zinc",
};

const ALL_LABELS: Record<AnyStatus, string> = {
    ...ORDER_STATUS_LABELS,
    ...TICKET_STATUS_LABELS,
};

interface StatusBadgeProps {
    status: AnyStatus;
    className?: string;
}

/**
 * @example
 * <StatusBadge status="IN_PREPARATION" />   // → amber "In Preparation"
 * <StatusBadge status="READY" />            // → green "Ready"
 */
export function StatusBadge({ status, className }: StatusBadgeProps) {
    return (
        <Badge variant={STATUS_VARIANT[status]} className={className}>
            {ALL_LABELS[status] ?? status}
        </Badge>
    );
}
