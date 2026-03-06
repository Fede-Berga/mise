/**
 * TypeScript types for the menu domain.
 * Mirrors the backend Pydantic schemas in services/menu-service/app/api/schemas.py.
 *
 * Keep in sync with backend changes. In a future iteration, these could be
 * auto-generated from OpenAPI specs via `openapi-typescript`.
 */

export interface MenuItem {
    id: number;
    tenant_id: string;
    name: string;
    description: string | null;
    price: number;
    category: string;
    is_available: boolean;
    created_at: string;
    updated_at: string;
}

export interface MenuItemCreate {
    name: string;
    description?: string | null;
    price: number;
    category?: string;
    is_available?: boolean;
}

export interface MenuItemUpdate {
    name?: string;
    description?: string | null;
    price?: number;
    category?: string;
    is_available?: boolean;
}
