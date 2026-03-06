/**
 * Menu service API client.
 * All functions proxy through Next.js to /api/menus → menu-service.
 *
 * The menu-service controller exposes flat /items routes (no restaurant nesting).
 * Multi-restaurant filtering will be added via query params in a future iteration.
 */

import { apiFetch } from "./client";
import type { MenuItem, MenuItemCreate, MenuItemUpdate } from "@/lib/types/menu";

const BASE = "/api/menus";

/** Fetch all menu items. */
export async function getMenuItems(): Promise<MenuItem[]> {
    return apiFetch<MenuItem[]>(`${BASE}/items`);
}

/** Fetch a single menu item. */
export async function getMenuItem(id: number): Promise<MenuItem> {
    return apiFetch<MenuItem>(`${BASE}/items/${id}`);
}

/** Create a new menu item. */
export async function createMenuItem(data: MenuItemCreate): Promise<MenuItem> {
    return apiFetch<MenuItem>(`${BASE}/items`, { method: "POST", body: data });
}

/** Partially update a menu item. */
export async function updateMenuItem(id: number, data: MenuItemUpdate): Promise<MenuItem> {
    return apiFetch<MenuItem>(`${BASE}/items/${id}`, { method: "PATCH", body: data });
}

/** Delete a menu item. */
export async function deleteMenuItem(id: number): Promise<void> {
    return apiFetch<void>(`${BASE}/items/${id}`, { method: "DELETE" });
}
