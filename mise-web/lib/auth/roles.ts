/**
 * Role-based access control utilities.
 *
 * Each role defines:
 *  - allowedRoutes: path prefixes the role can visit
 *  - defaultRoute:  where to land after login
 */

import type { MiseRole } from "./types";

interface RoleConfig {
    allowedRoutes: string[];
    defaultRoute: string;
    canEditMenu: boolean;
    canManageSettings: boolean;
}

export const ROLE_CONFIG: Record<MiseRole, RoleConfig> = {
    owner: {
        allowedRoutes: ["/dashboard", "/menu", "/orders", "/kitchen", "/settings"],
        defaultRoute: "/dashboard",
        canEditMenu: true,
        canManageSettings: true,
    },
    manager: {
        allowedRoutes: ["/dashboard", "/menu", "/orders", "/kitchen"],
        defaultRoute: "/dashboard",
        canEditMenu: true,
        canManageSettings: false,
    },
    chef: {
        allowedRoutes: ["/kitchen"],
        defaultRoute: "/kitchen",
        canEditMenu: false,
        canManageSettings: false,
    },
    waiter: {
        allowedRoutes: ["/orders"],
        defaultRoute: "/orders",
        canEditMenu: false,
        canManageSettings: false,
    },
    cashier: {
        allowedRoutes: ["/orders"],
        defaultRoute: "/orders",
        canEditMenu: false,
        canManageSettings: false,
    },
};

/** Returns true if the role is allowed to visit the given pathname. */
export function canAccess(role: MiseRole, pathname: string): boolean {
    return ROLE_CONFIG[role].allowedRoutes.some((r) => pathname.startsWith(r));
}

/** Returns the default landing route for a role after login. */
export function getDefaultRoute(role: MiseRole): string {
    return ROLE_CONFIG[role].defaultRoute;
}

/** Returns true if the role can create/edit/delete menu items. */
export function canEditMenu(role: MiseRole): boolean {
    return ROLE_CONFIG[role].canEditMenu;
}

/** Returns true if the role can access settings. */
export function canManageSettings(role: MiseRole): boolean {
    return ROLE_CONFIG[role].canManageSettings;
}
