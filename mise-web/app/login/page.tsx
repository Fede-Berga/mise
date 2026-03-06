/**
 * Login page — redirects to Keycloak via NextAuth signIn.
 * The actual login form is on Keycloak; this page is just a landing
 * that triggers the OAuth2 redirect.
 */

"use client";

import { signIn, useSession } from "next-auth/react";
import { Suspense, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";

function LoginPageContent() {
    const { status } = useSession();
    const router = useRouter();
    const searchParams = useSearchParams();
    const callbackUrl = searchParams.get("callbackUrl") ?? "/dashboard";

    useEffect(() => {
        if (status === "authenticated") {
            router.replace(callbackUrl);
        }
    }, [status, callbackUrl, router]);

    return (
        <div className="flex h-screen items-center justify-center bg-mise-bg">
            <div className="text-center px-6">
                <div className="font-display text-5xl font-bold text-mise-amber tracking-tight">mise</div>
                <p className="mt-2 text-mise-text-muted text-sm">Everything in its place.</p>
                <p className="mt-4 text-mise-text-faint text-sm">
                    {status === "authenticated"
                        ? "Signing you in…"
                        : "Click below to continue to secure login."}
                </p>
                {status !== "authenticated" && (
                    <div className="mt-6 flex justify-center">
                        <button
                            type="button"
                            onClick={() => signIn("keycloak", { callbackUrl })}
                            className="inline-flex items-center rounded-md bg-mise-amber px-4 py-2 text-sm font-semibold text-black shadow-sm hover:bg-mise-amber-light focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-mise-amber"
                        >
                            Continue with Keycloak
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
}

export default function LoginPage() {
    return (
        <Suspense fallback={null}>
            <LoginPageContent />
        </Suspense>
    );
}
