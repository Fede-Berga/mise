/**
 * Order service API client.
 * All functions proxy through Next.js to /api/orders → order-service.
 */

import { apiFetch } from "./client";
import type { Order, OrderCreate, OrderStatus, OrderStatusUpdate } from "@/lib/types/orders";

const BASE = "/api/orders";

/** Fetch all orders, optionally filtered by status. */
export async function getOrders(status?: OrderStatus): Promise<Order[]> {
    const qs = status ? `?status=${status}` : "";
    return apiFetch<Order[]>(`${BASE}/${qs}`);
}

/** Fetch a single order by id. */
export async function getOrder(id: number): Promise<Order> {
    return apiFetch<Order>(`${BASE}/${id}`);
}

/** Place a new order. */
export async function createOrder(data: OrderCreate): Promise<Order> {
    return apiFetch<Order>(`${BASE}/`, { method: "POST", body: data });
}

/** Advance an order to a new status. */
export async function updateOrderStatus(id: number, status: OrderStatus): Promise<Order> {
    const body: OrderStatusUpdate = { status };
    return apiFetch<Order>(`${BASE}/${id}/status`, { method: "PATCH", body });
}
