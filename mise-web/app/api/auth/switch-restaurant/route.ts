/**
 * Restaurant switcher API route — updates the active restaurant in the JWT.
 * Only callable by owners (validated via session role check).
 */

import { NextRequest, NextResponse } from "next/server";
import { getServerSession } from "next-auth/next";
import { authOptions } from "@/lib/auth/options";
import type { MiseSession } from "@/lib/auth/types";

export async function POST(req: NextRequest) {
    const session = (await getServerSession(authOptions)) as MiseSession | null;

    if (!session) {
        return NextResponse.json({ error: "unauthenticated" }, { status: 401 });
    }

    if (session.user.role !== "owner") {
        return NextResponse.json({ error: "forbidden" }, { status: 403 });
    }

    const { restaurantId } = await req.json() as { restaurantId?: string };

    if (!restaurantId || !session.user.restaurantIds.includes(restaurantId)) {
        return NextResponse.json({ error: "invalid_restaurant" }, { status: 400 });
    }

    // The JWT is httpOnly — we can't update it here directly.
    // Return the new active ID so the client can re-trigger signIn or
    // store it in a cookie that the middleware reads.
    const res = NextResponse.json({ ok: true, activeRestaurantId: restaurantId });
    res.cookies.set("mise-active-restaurant", restaurantId, {
        httpOnly: true,
        sameSite: "lax",
        path: "/",
        maxAge: 60 * 60 * 24 * 7, // 7 days
    });
    return res;
}
