import type { NextAuthOptions } from "next-auth";
import type { JWT } from "next-auth/jwt";
import type { MiseRole, MiseSession } from "@/lib/auth/types";
import KeycloakProvider from "next-auth/providers/keycloak";

function decodeJwtPayload(token: string): Record<string, unknown> | null {
    try {
        const [, payload] = token.split(".");
        if (!payload) return null;
        const padded = payload.padEnd(payload.length + (4 - (payload.length % 4)) % 4, "=");
        const json = Buffer.from(padded, "base64").toString("utf8");
        return JSON.parse(json);
    } catch {
        return null;
    }
}

const ROLE_PRIORITY: MiseRole[] = ["owner", "manager", "chef", "cashier", "waiter"];

function extractTokenRoles(claims: Record<string, unknown>, clientId: string): string[] {
    const realmAccess = claims["realm_access"] as { roles?: string[] } | undefined;
    const realmRoles = Array.isArray(realmAccess?.roles) ? realmAccess.roles : [];

    const resourceAccess = claims["resource_access"] as Record<string, { roles?: string[] }> | undefined;
    const clientRoles = Array.isArray(resourceAccess?.[clientId]?.roles) ? resourceAccess?.[clientId]?.roles ?? [] : [];

    return [...new Set([...realmRoles, ...clientRoles].map((r) => r.toLowerCase()))];
}

function resolveRole(roles: string[]): MiseRole {
    for (const role of ROLE_PRIORITY) {
        if (roles.includes(role)) return role;
    }
    return "waiter";
}

const nextAuthDebugEnabled = (process.env.NEXTAUTH_DEBUG ?? "false").toLowerCase() === "true";

function resolveAccessTokenExpiry(account?: { expires_at?: number }, accessToken?: string): number {
    if (account?.expires_at) {
        return account.expires_at * 1000;
    }
    const claims = accessToken ? decodeJwtPayload(accessToken) : null;
    const exp = claims?.exp;
    if (typeof exp === "number") {
        return exp * 1000;
    }
    return Date.now() + 5 * 60 * 1000;
}

async function refreshAccessToken(token: JWT): Promise<JWT> {
    try {
        if (!token.refreshToken) {
            return { ...token, error: "RefreshAccessTokenError" };
        }

        const issuer = process.env.KEYCLOAK_ISSUER ?? "http://localhost:8080/auth/realms/mise";
        const tokenUrl = `${issuer.replace(/\/$/, "")}/protocol/openid-connect/token`;

        const body = new URLSearchParams({
            grant_type: "refresh_token",
            client_id: process.env.KEYCLOAK_CLIENT_ID ?? "mise-web",
            client_secret: process.env.KEYCLOAK_CLIENT_SECRET ?? "mise-web-secret",
            refresh_token: token.refreshToken,
        });

        const response = await fetch(tokenUrl, {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body,
            cache: "no-store",
        });

        if (!response.ok) {
            throw new Error(`refresh_failed_${response.status}`);
        }

        const refreshed = await response.json() as {
            access_token: string;
            expires_in: number;
            refresh_token?: string;
        };

        return {
            ...token,
            accessToken: refreshed.access_token,
            accessTokenExpires: Date.now() + refreshed.expires_in * 1000,
            refreshToken: refreshed.refresh_token ?? token.refreshToken,
            error: undefined,
        };
    } catch {
        return { ...token, error: "RefreshAccessTokenError" };
    }
}

export const authOptions: NextAuthOptions = {
    // Stable secret for both NextAuth and middleware/getToken
    secret: process.env.NEXTAUTH_SECRET ?? "mise-dev-secret",
    providers: [
        KeycloakProvider({
            clientId: process.env.KEYCLOAK_CLIENT_ID ?? "mise-web",
            clientSecret: process.env.KEYCLOAK_CLIENT_SECRET ?? "mise-web-secret",
            issuer: process.env.KEYCLOAK_ISSUER ?? "http://localhost:8080/auth/realms/mise",
        }),
    ],
    session: { strategy: "jwt" },
    callbacks: {
        async jwt({ token, account }) {
            // On first sign-in, derive role + restaurants from ID/access token claims.
            if (account && (account.id_token || account.access_token)) {
                const clientId = process.env.KEYCLOAK_CLIENT_ID ?? "mise-web";
                const idClaims = account.id_token ? (decodeJwtPayload(account.id_token) ?? {}) : {};
                const accessClaims = account.access_token ? (decodeJwtPayload(account.access_token) ?? {}) : {};
                const role = resolveRole(extractTokenRoles(idClaims, clientId).concat(extractTokenRoles(accessClaims, clientId)));

                const rawIds = idClaims["restaurant_ids"] ?? accessClaims["restaurant_ids"];
                const restaurantIds: string[] = Array.isArray(rawIds)
                    ? (rawIds as string[])
                    : typeof rawIds === "string"
                        ? (rawIds as string).split(",").map((s) => s.trim()).filter(Boolean)
                        : [];

                token.role = role;
                token.restaurantIds = restaurantIds;
                token.activeRestaurantId = restaurantIds[0] ?? (token.activeRestaurantId as string | undefined) ?? "restaurant-0001";
                token.accessToken = account.access_token as string;
                token.accessTokenExpires = resolveAccessTokenExpiry(account, account.access_token ?? undefined);
                token.refreshToken = account.refresh_token;
                token.error = undefined;
                return token;
            }

            if (Date.now() < ((token.accessTokenExpires as number | undefined) ?? 0) - 60_000) {
                return token;
            }

            return refreshAccessToken(token);
        },
        async session({ session, token }) {
            const s = session as MiseSession;
            const roleFromToken = token.role as MiseRole | undefined;
            s.user = {
                ...s.user,
                // If the token doesn't carry a role yet, keep whatever was already on the session.
                role: roleFromToken ?? (s.user.role as MiseRole),
                restaurantIds: (token.restaurantIds as string[]) ?? [],
                activeRestaurantId: (token.activeRestaurantId as string) ?? "",
                accessToken: (token.accessToken as string) ?? "",
            };
            return s;
        },
    },
    debug: nextAuthDebugEnabled,
};
