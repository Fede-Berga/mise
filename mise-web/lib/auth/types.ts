/**
 * Typed session and JWT shapes for the Mise cockpit.
 */

import type { DefaultSession } from "next-auth";
import type { DefaultJWT } from "next-auth/jwt";

export type MiseRole = "owner" | "manager" | "chef" | "waiter" | "cashier";

declare module "next-auth" {
    interface Session extends DefaultSession {
        user: DefaultSession["user"] & {
            role: MiseRole;
            restaurantIds: string[];
            activeRestaurantId: string;
            accessToken: string;
        };
    }
}

declare module "next-auth/jwt" {
    interface JWT extends DefaultJWT {
        role: MiseRole;
        restaurantIds: string[];
        activeRestaurantId: string;
        accessToken: string;
        accessTokenExpires?: number;
        refreshToken?: string;
        error?: "RefreshAccessTokenError";
    }
}

export interface MiseSession {
    user: {
        name?: string | null;
        email?: string | null;
        image?: string | null;
        role: MiseRole;
        restaurantIds: string[];
        activeRestaurantId: string;
        accessToken: string;
    };
    expires: string;
}
