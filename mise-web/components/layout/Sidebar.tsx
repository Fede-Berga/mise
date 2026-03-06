/**
 * Sidebar — fixed left navigation, filtered by the user's role.
 */

"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useSession } from "next-auth/react";
import {
    LayoutDashboard,
    UtensilsCrossed,
    ClipboardList,
    ChefHat,
    Users,
    BarChart2,
    Settings,
    type LucideIcon,
} from "lucide-react";
import { clsx } from "clsx";
import { canAccess } from "@/lib/auth/roles";
import type { MiseRole } from "@/lib/auth/types";

interface NavItem {
    label: string;
    href: string;
    icon: LucideIcon;
    comingSoon?: boolean;
}

const allNavItems: NavItem[] = [
    { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
    { label: "Menu", href: "/menu", icon: UtensilsCrossed },
    { label: "Orders", href: "/orders", icon: ClipboardList },
    { label: "Kitchen", href: "/kitchen", icon: ChefHat },
    { label: "Personnel", href: "/personnel", icon: Users, comingSoon: true },
    { label: "Analytics", href: "/analytics", icon: BarChart2, comingSoon: true },
    { label: "Settings", href: "/settings", icon: Settings, comingSoon: true },
];

export function Sidebar() {
    const pathname = usePathname();
    const { data: session, status } = useSession();
    const role = session?.user?.role as MiseRole | undefined;

    // Only show items the role can access (coming-soon items are always shown for roadmap visibility).
    // While the session is loading, show all items so the shell renders quickly.
    const visibleItems = allNavItems.filter((item) => {
        if (item.comingSoon) return true;
        if (!role || status !== "authenticated") return true;
        return canAccess(role, item.href);
    });

    return (
        <aside className="fixed inset-y-0 left-0 z-40 flex w-60 flex-col bg-mise-surface border-r border-mise-border">
            {/* Brand mark */}
            <div className="flex items-center gap-3 px-5 py-5 border-b border-mise-border shrink-0">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-mise-amber">
                    <span className="font-display font-bold text-neutral-950 text-base leading-none">M</span>
                </div>
                <span className="font-display text-lg font-bold tracking-tight text-mise-text lowercase">
                    mise
                </span>
            </div>

            {/* Navigation */}
            <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-0.5" aria-label="Main navigation">
                {visibleItems.map((item) => {
                    const isActive = pathname.startsWith(item.href);
                    const Icon = item.icon;

                    if (item.comingSoon) {
                        return (
                            <div
                                key={item.href}
                                className="flex items-center gap-3 rounded-lg px-3 py-2 text-mise-text-faint cursor-not-allowed select-none"
                                title="Coming soon"
                            >
                                <Icon size={17} className="shrink-0" />
                                <span className="text-sm">{item.label}</span>
                                <span className="ml-auto text-[10px] bg-neutral-800 text-neutral-500 rounded px-1.5 py-0.5">
                                    Soon
                                </span>
                            </div>
                        );
                    }

                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={clsx(
                                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors duration-100",
                                isActive
                                    ? "bg-mise-amber/10 text-mise-amber font-medium"
                                    : "text-mise-text-muted hover:bg-mise-raised hover:text-mise-text",
                            )}
                        >
                            <Icon size={17} className={clsx("shrink-0", isActive && "text-mise-amber")} />
                            {item.label}
                            {isActive && (
                                <span className="ml-auto h-1.5 w-1.5 rounded-full bg-mise-amber shrink-0" />
                            )}
                        </Link>
                    );
                })}
            </nav>

            {/* Footer: role badge */}
            <div className="px-5 py-4 border-t border-mise-border flex items-center justify-between">
                <p className="text-xs text-mise-text-faint">v0.1.0 · MVP</p>
                {role && status === "authenticated" && (
                    <span className="text-[10px] uppercase tracking-widest font-medium text-mise-amber/70 bg-mise-amber/10 rounded px-1.5 py-0.5">
                        {role}
                    </span>
                )}
            </div>
        </aside>
    );
}
