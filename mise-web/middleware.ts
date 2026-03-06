/**
 * Next.js Edge Middleware — auth guard + role-based route protection.
 *
 * Runs before every request to /(cockpit) routes and /api/* (except auth).
 * - Unauthenticated users → /login
 * - Authenticated users on a forbidden route → their default route
 * - Injects X-Tenant-Id on API requests from the active restaurant in session
 */

import { getToken } from "next-auth/jwt";
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { canAccess, getDefaultRoute } from "@/lib/auth/roles";
import type { MiseRole } from "@/lib/auth/types";

const PUBLIC_PATHS = ["/login", "/api/auth"];

export async function middleware(req: NextRequest) {
    const { pathname } = req.nextUrl;

    // Allow public paths through
    if (PUBLIC_PATHS.some((p) => pathname.startsWith(p))) {
        return NextResponse.next();
    }

    // Use the same secret as NextAuth so we can read its JWT
    const token = await getToken({
        req,
        secret: process.env.NEXTAUTH_SECRET ?? "mise-dev-secret",
    });

    // Not authenticated or missing API bearer token → redirect to login
    if (!token || !token.accessToken) {
        const loginUrl = req.nextUrl.clone();
        loginUrl.pathname = "/login";
        loginUrl.searchParams.set("callbackUrl", pathname);
        return NextResponse.redirect(loginUrl);
    }

    const role = (token.role as MiseRole) ?? "waiter";
    const activeRestaurantId = req.cookies.get("mise-active-restaurant")?.value
        ?? (token.activeRestaurantId as string | undefined);

    // API proxy requests — inject X-Tenant-Id
    if (pathname.startsWith("/api/")) {
        if (!activeRestaurantId) {
            return NextResponse.json({ error: "missing_active_restaurant" }, { status: 400 });
        }
        const headers = new Headers(req.headers);
        headers.set("X-Tenant-Id", activeRestaurantId);
        return NextResponse.next({ request: { headers } });
    }

    // Check role-based access for cockpit routes
    if (!canAccess(role, pathname)) {
        const defaultUrl = req.nextUrl.clone();
        defaultUrl.pathname = getDefaultRoute(role);
        return NextResponse.redirect(defaultUrl);
    }

    return NextResponse.next();
}

export const config = {
    matcher: [
        // Match all cockpit routes and API routes except static assets
        "/((?!_next/static|_next/image|favicon.ico).*)",
    ],
};
