/**
 * Auth session helpers — thin wrappers around NextAuth for type safety.
 */

import { getServerSession as _getServerSession } from "next-auth/next";
import { authOptions } from "@/lib/auth/options";
import type { MiseSession } from "./types";

/** Server-side: returns the typed session or null. */
export async function getServerSession(): Promise<MiseSession | null> {
    return _getServerSession(authOptions) as Promise<MiseSession | null>;
}

/**
 * NextAuth providers array — exported for use in SessionProvider.
 * Also re-exports authOptions for convenience.
 */
export { authOptions };
