/**
 * TypeScript types for the order domain.
 * Mirrors services/order-service/app/api/schemas.py.
 */

export type OrderStatus = "NEW" | "IN_PREPARATION" | "READY" | "CLOSED";

export interface OrderItem {
    id: number;
    menu_item_id: number;
    quantity: number;
    unit_price: number;
    line_total: number;
}

export interface Order {
    id: number;
    tenant_id: string;
    restaurant_id: string;
    table_id: number | null;
    status: OrderStatus;
    total_amount: number;
    notes: string | null;
    items: OrderItem[];
    created_at: string;
    updated_at: string;
}

export interface OrderItemCreate {
    menu_item_id: number;
    quantity: number;
}

export interface OrderCreate {
    restaurant_id: string;
    table_id?: number | null;
    items: OrderItemCreate[];
    notes?: string | null;
}

export interface OrderStatusUpdate {
    status: OrderStatus;
}

/** Human-readable label map for order statuses */
export const ORDER_STATUS_LABELS: Record<OrderStatus, string> = {
    NEW: "New",
    IN_PREPARATION: "In Preparation",
    READY: "Ready",
    CLOSED: "Closed",
};
