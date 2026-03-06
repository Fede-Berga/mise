/**
 * Kitchen service API client.
 * All functions proxy through Next.js to /api/kitchen → kitchen-service.
 */

import { apiFetch } from "./client";
import type { KitchenTicket, KitchenTicketCreate, TicketStatus, TicketStatusUpdate } from "@/lib/types/kitchen";

const BASE = "/api/kitchen";

/** Fetch kitchen tickets, optionally filtered by status. */
export async function getTickets(status?: TicketStatus): Promise<KitchenTicket[]> {
    const qs = status ? `?status=${status}` : "";
    return apiFetch<KitchenTicket[]>(`${BASE}/tickets${qs}`);
}

/** Fetch a single ticket by id. */
export async function getTicket(id: number): Promise<KitchenTicket> {
    return apiFetch<KitchenTicket>(`${BASE}/tickets/${id}`);
}

/** Create a kitchen ticket (typically triggered by order placement). */
export async function createTicket(data: KitchenTicketCreate): Promise<KitchenTicket> {
    return apiFetch<KitchenTicket>(`${BASE}/tickets/`, { method: "POST", body: data });
}

/** Advance a ticket's status (forward-only state machine). */
export async function advanceTicketStatus(id: number, status: TicketStatus): Promise<KitchenTicket> {
    const body: TicketStatusUpdate = { status };
    return apiFetch<KitchenTicket>(`${BASE}/tickets/${id}/status`, { method: "PATCH", body });
}
