/**
 * Catch-all proxy route handler.
 *
 * Forwards /api/<service>/<path> to the correct microservice,
 * reading service URLs from env vars at request time (not build time).
 *
 * Env vars (with defaults for local dev):
 *   RESTAURANT_SVC_URL  → http://localhost:8001
 *   MENU_SVC_URL        → http://localhost:8002
 *   ORDER_SVC_URL       → http://localhost:8003
 *   KITCHEN_SVC_URL     → http://localhost:8004
 */

import { NextRequest, NextResponse } from "next/server";
import { getServerSession } from "next-auth";

import { authOptions } from "@/lib/auth/options";
import type { MiseSession } from "@/lib/auth/types";

const SERVICE_MAP: Record<string, string> = {
    restaurants: process.env.RESTAURANT_SVC_URL ?? "http://localhost:8001",
    menus: process.env.MENU_SVC_URL ?? "http://localhost:8002",
    orders: process.env.ORDER_SVC_URL ?? "http://localhost:8003",
    kitchen: process.env.KITCHEN_SVC_URL ?? "http://localhost:8004",
};

export async function GET(req: NextRequest, { params }: { params: { path: string[] } }) {
    return proxy(req, params.path, "GET");
}
export async function POST(req: NextRequest, { params }: { params: { path: string[] } }) {
    return proxy(req, params.path, "POST");
}
export async function PATCH(req: NextRequest, { params }: { params: { path: string[] } }) {
    return proxy(req, params.path, "PATCH");
}
export async function DELETE(req: NextRequest, { params }: { params: { path: string[] } }) {
    return proxy(req, params.path, "DELETE");
}

async function proxy(req: NextRequest, pathSegments: string[], method: string) {
    // pathSegments: ["restaurants", "..."] or ["menus", "items", "1"]
    const [service, ...rest] = pathSegments;
    const base = SERVICE_MAP[service];

    if (!base) {
        return NextResponse.json({ error: `Unknown service: ${service}` }, { status: 502 });
    }

    const upstreamPath = `/${service}/${rest.join("/")}${req.nextUrl.search}`;
    const url = `${base}${upstreamPath}`;

    const body = method !== "GET" && method !== "DELETE" ? await req.text() : undefined;

    const headers: Record<string, string> = {};
    const contentType = req.headers.get("content-type");
    if (contentType) {
        headers["Content-Type"] = contentType;
    }

    const session = (await getServerSession(authOptions)) as MiseSession | null;
    const accessToken = session?.user?.accessToken;
    if (!accessToken) {
        return NextResponse.json({ error: "missing_access_token" }, { status: 401 });
    }
    const cookieTenant = req.cookies.get("mise-active-restaurant")?.value;
    const sessionTenant = cookieTenant
        ?? session?.user?.activeRestaurantId;
    if (!sessionTenant) {
        return NextResponse.json({ error: "missing_active_restaurant" }, { status: 400 });
    }
    headers["X-Tenant-Id"] = sessionTenant;
    headers["Authorization"] = `Bearer ${accessToken}`;

    try {
        const upstream = await fetch(url, { method, headers, body });
        const text = await upstream.text();
        return new NextResponse(text, {
            status: upstream.status,
            headers: { "Content-Type": upstream.headers.get("Content-Type") ?? "application/json" },
        });
    } catch (err) {
        console.error(`Proxy error → ${url}:`, err);
        return NextResponse.json({ error: "upstream_unavailable" }, { status: 502 });
    }
}
