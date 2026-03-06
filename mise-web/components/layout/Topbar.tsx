/**
 * Topbar — fixed top bar with restaurant switcher, user info, and logout.
 */

"use client";

import { Bell, LogOut } from "lucide-react";
import { useSession, signOut } from "next-auth/react";
import { RestaurantSwitcher } from "@/components/auth/RestaurantSwitcher";

export function Topbar() {
    const { data: session } = useSession();
    const user = session?.user;
    const initials = user?.name
        ? user.name.split(" ").map((n) => n[0]).join("").toUpperCase().slice(0, 2)
        : "M";

    return (
        <header className="sticky top-0 z-30 flex h-14 items-center justify-between border-b border-mise-border bg-mise-bg/80 backdrop-blur-sm px-6">
            {/* Left: restaurant switcher (owners only) + breadcrumb slot */}
            <div className="flex items-center gap-3">
                <RestaurantSwitcher />
                <div id="topbar-title" />
            </div>

            {/* Right: actions */}
            <div className="flex items-center gap-3">
                {/* Notification bell */}
                <button
                    aria-label="Notifications"
                    className="relative rounded-lg p-2 text-mise-text-muted hover:bg-mise-raised hover:text-mise-text transition-colors"
                >
                    <Bell size={18} />
                </button>

                {/* User avatar + name + logout */}
                <div className="flex items-center gap-2">
                    {user?.name && (
                        <span className="hidden sm:block text-sm text-mise-text-muted">{user.name}</span>
                    )}
                    <div className="h-8 w-8 rounded-full bg-mise-amber/20 border border-mise-amber/40 flex items-center justify-center">
                        <span className="text-mise-amber text-xs font-semibold">{initials}</span>
                    </div>
                    <button
                        onClick={() => signOut({ callbackUrl: "/login" })}
                        aria-label="Sign out"
                        className="rounded-lg p-2 text-mise-text-faint hover:bg-mise-raised hover:text-red-400 transition-colors"
                    >
                        <LogOut size={16} />
                    </button>
                </div>
            </div>
        </header>
    );
}
