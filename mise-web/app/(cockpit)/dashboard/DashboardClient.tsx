/**
 * DashboardClient — live data layer for the dashboard.
 * Polls orders every 5 seconds to keep KPIs fresh.
 */

"use client";

import { useOrders } from "@/hooks/useOrders";
import { useKitchenTickets } from "@/hooks/useKitchenTickets";
import { Card } from "@/components/ui/Card";
import { Spinner } from "@/components/ui/Spinner";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { formatCurrency } from "@/lib/utils/currency";
import { formatRelative } from "@/lib/utils/date";
import type { Order } from "@/lib/types/orders";
import { ShoppingBag, ChefHat, DollarSign, Clock } from "lucide-react";

// ─── KPI Card ────────────────────────────────────────────────────────────────

interface KpiCardProps {
    icon: React.ReactNode;
    label: string;
    value: string | number;
    sub?: string;
    accent?: boolean;
}

function KpiCard({ icon, label, value, sub, accent }: KpiCardProps) {
    return (
        <Card className="flex items-start gap-4 transition-colors duration-150">
            <div className={`p-2.5 rounded-xl ${accent ? "bg-mise-amber/15 text-mise-amber" : "bg-mise-raised text-mise-text-muted"}`}>
                {icon}
            </div>
            <div className="flex-1 min-w-0">
                <p className="text-xs text-mise-text-muted uppercase tracking-wide">{label}</p>
                <p className="mt-1 text-2xl font-bold text-mise-text tabular-nums">{value}</p>
                {sub && <p className="text-xs text-mise-text-faint mt-0.5">{sub}</p>}
            </div>
        </Card>
    );
}

// ─── Recent Orders Table ──────────────────────────────────────────────────────

function RecentOrderRow({ order }: { order: Order }) {
    return (
        <tr className="border-t border-mise-border hover:bg-mise-raised/50 transition-colors">
            <td className="px-4 py-3 text-xs font-mono text-mise-text-muted">#{order.id}</td>
            <td className="px-4 py-3 text-sm text-mise-text">{order.restaurant_id}</td>
            <td className="px-4 py-3">
                <StatusBadge status={order.status} />
            </td>
            <td className="px-4 py-3 text-sm font-semibold text-mise-text text-right">
                {formatCurrency(order.total_amount)}
            </td>
            <td className="px-4 py-3 text-xs text-mise-text-muted text-right">
                {formatRelative(order.created_at)}
            </td>
        </tr>
    );
}

// ─── Main component ───────────────────────────────────────────────────────────

export function DashboardClient() {
    const { orders, isLoading: ordersLoading } = useOrders();
    const { tickets, isLoading: ticketsLoading } = useKitchenTickets();

    const openOrders = orders.filter((o) => o.status !== "CLOSED");
    const todayRevenue = orders
        .filter((o) => o.status === "CLOSED")
        .reduce((sum, o) => sum + o.total_amount, 0);
    const openTickets = tickets.filter((t) => t.status !== "DONE");

    return (
        <div className="flex flex-col gap-6">
            {/* ── KPI Grid ────────────────────────────────────────────────── */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <KpiCard
                    icon={<ShoppingBag size={20} />}
                    label="Open orders"
                    value={ordersLoading ? "—" : openOrders.length}
                    sub="Across all statuses"
                    accent
                />
                <KpiCard
                    icon={<ChefHat size={20} />}
                    label="Kitchen tickets"
                    value={ticketsLoading ? "—" : openTickets.length}
                    sub="Not yet done"
                />
                <KpiCard
                    icon={<DollarSign size={20} />}
                    label="Today's revenue"
                    value={ordersLoading ? "—" : formatCurrency(todayRevenue)}
                    sub="Closed orders only"
                    accent
                />
                <KpiCard
                    icon={<Clock size={20} />}
                    label="Total orders today"
                    value={ordersLoading ? "—" : orders.length}
                    sub="All statuses"
                />
            </div>

            {/* ── Recent Orders ────────────────────────────────────────────── */}
            <Card padding={false}>
                <div className="px-5 py-4 border-b border-mise-border flex items-center justify-between">
                    <h2 className="text-sm font-semibold text-mise-text">Recent orders</h2>
                    {ordersLoading && <Spinner size="sm" />}
                </div>
                {orders.length === 0 && !ordersLoading ? (
                    <div className="px-5 py-16 text-center">
                        <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-xl bg-mise-raised text-mise-text-muted">
                            <ShoppingBag size={24} strokeWidth={1.5} />
                        </div>
                        <p className="text-sm font-medium text-mise-text">No orders yet</p>
                        <p className="mt-1 text-xs text-mise-text-muted">Orders will appear here when placed.</p>
                    </div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="w-full text-left">
                            <thead>
                                <tr>
                                    {["#", "Restaurant", "Status", "Total", "Time"].map((h, i) => (
                                        <th key={h} className={`px-4 py-2.5 text-[10px] font-medium uppercase tracking-wider text-mise-text-faint ${i >= 3 ? "text-right" : ""}`}>{h}</th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {orders.slice(0, 10).map((o) => <RecentOrderRow key={o.id} order={o} />)}
                            </tbody>
                        </table>
                    </div>
                )}
            </Card>
        </div>
    );
}
