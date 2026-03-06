/**
 * TypeScript types for the kitchen domain.
 * Mirrors services/kitchen-service/app/api/schemas.py.
 */

export type TicketStatus = "NEW" | "PREPARING" | "READY" | "DONE";

export interface TicketItem {
    id: number;
    menu_item_id: number;
    menu_item_name: string;
    quantity: number;
    notes: string | null;
}

export interface KitchenTicket {
    id: number;
    tenant_id: string;
    order_id: number;
    restaurant_id: string;
    table_label: string | null;
    status: TicketStatus;
    items: TicketItem[];
    created_at: string;
    updated_at: string;
}

export interface KitchenTicketCreate {
    order_id: number;
    restaurant_id: string;
    table_label?: string | null;
    items: Omit<TicketItem, "id">[];
}

export interface TicketStatusUpdate {
    status: TicketStatus;
}

/** Forward-only transition map: current status → next allowed status */
export const TICKET_NEXT_STATUS: Partial<Record<TicketStatus, TicketStatus>> = {
    NEW: "PREPARING",
    PREPARING: "READY",
    READY: "DONE",
};

export const TICKET_STATUS_LABELS: Record<TicketStatus, string> = {
    NEW: "New",
    PREPARING: "Preparing",
    READY: "Ready",
    DONE: "Done",
};
