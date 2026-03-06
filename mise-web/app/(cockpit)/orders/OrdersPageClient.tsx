/**
 * OrdersPageClient — live Kanban board with integrated order entry.
 *
 * Features:
 * - Four status columns (NEW | IN_PREPARATION | READY | CLOSED)
 * - Manual status advancement
 * - Enterprise order entry modal with multi-line items and validation
 */

"use client";

import { useEffect, useMemo, useState } from "react";
import { useSession } from "next-auth/react";
import { Plus, Trash2 } from "lucide-react";
import { clsx } from "clsx";

import { useOrders } from "@/hooks/useOrders";
import { useMenuItems } from "@/hooks/useMenuItems";
import { createOrder, updateOrderStatus } from "@/lib/api/orders";
import type { Order, OrderStatus } from "@/lib/types/orders";
import { ORDER_STATUS_LABELS } from "@/lib/types/orders";
import { formatCurrency } from "@/lib/utils/currency";

import { OrderCard } from "@/components/domain/orders/OrderCard";
import { Spinner } from "@/components/ui/Spinner";
import { Button } from "@/components/ui/Button";
import { Modal } from "@/components/ui/Modal";
import { Input } from "@/components/ui/Input";

const COLUMNS: OrderStatus[] = ["NEW", "IN_PREPARATION", "READY", "CLOSED"];

const COLUMN_COLORS: Record<OrderStatus, string> = {
    NEW: "border-t-indigo-500",
    IN_PREPARATION: "border-t-amber-500",
    READY: "border-t-green-500",
    CLOSED: "border-t-zinc-600",
};

interface DraftLine {
    id: string;
    menuItemId: number | "";
    quantity: number;
}

function newLine(seed = ""): DraftLine {
    return { id: `${Date.now()}-${Math.random()}-${seed}`, menuItemId: "", quantity: 1 };
}

export function OrdersPageClient() {
    const { data: session } = useSession();
    const { orders, isLoading, error, mutate } = useOrders();
    const { items: menuItems, isLoading: menuLoading } = useMenuItems();

    const activeRestaurant = session?.user?.activeRestaurantId ?? "restaurant-0001";

    const [advancing, setAdvancing] = useState<number | null>(null);
    const [createOpen, setCreateOpen] = useState(false);
    const [creating, setCreating] = useState(false);
    const [createError, setCreateError] = useState<string | null>(null);

    const [restaurantId, setRestaurantId] = useState(activeRestaurant);
    const [tableId, setTableId] = useState("");
    const [notes, setNotes] = useState("");
    const [lines, setLines] = useState<DraftLine[]>([newLine("initial")]);

    useEffect(() => {
        if (!restaurantId || restaurantId === "restaurant-0001") {
            setRestaurantId(activeRestaurant);
        }
    }, [activeRestaurant, restaurantId]);

    useEffect(() => {
        if (menuItems.length === 0) return;
        setLines((prev) => prev.map((line, idx) => {
            if (line.menuItemId !== "") return line;
            if (idx !== 0) return line;
            return { ...line, menuItemId: menuItems[0].id };
        }));
    }, [menuItems]);

    const menuMap = useMemo(
        () => new Map(menuItems.map((item) => [item.id, item])),
        [menuItems],
    );

    const estimatedTotal = useMemo(() => lines.reduce((sum, line) => {
        if (line.menuItemId === "") return sum;
        const item = menuMap.get(line.menuItemId);
        return sum + (item?.price ?? 0) * line.quantity;
    }, 0), [lines, menuMap]);

    async function handleAdvance(order: Order, nextStatus: OrderStatus) {
        setAdvancing(order.id);
        try {
            await updateOrderStatus(order.id, nextStatus);
            await mutate();
        } finally {
            setAdvancing(null);
        }
    }

    function resetOrderForm() {
        setRestaurantId(activeRestaurant);
        setTableId("");
        setNotes("");
        setLines([{ ...newLine("reset"), menuItemId: menuItems[0]?.id ?? "" }]);
        setCreateError(null);
    }

    function openCreateModal() {
        resetOrderForm();
        setCreateOpen(true);
    }

    function addLine() {
        setLines((prev) => [...prev, { ...newLine("add"), menuItemId: menuItems[0]?.id ?? "" }]);
    }

    function removeLine(lineId: string) {
        setLines((prev) => {
            if (prev.length <= 1) return prev;
            return prev.filter((line) => line.id !== lineId);
        });
    }

    function updateLine(lineId: string, next: Partial<DraftLine>) {
        setLines((prev) => prev.map((line) => (line.id === lineId ? { ...line, ...next } : line)));
    }

    async function handleCreateOrder() {
        if (!restaurantId.trim()) {
            setCreateError("Restaurant Id is required.");
            return;
        }
        if (lines.length === 0) {
            setCreateError("Add at least one order item.");
            return;
        }
        if (lines.some((line) => line.menuItemId === "" || line.quantity < 1)) {
            setCreateError("Each order line needs a menu item and quantity >= 1.");
            return;
        }

        const aggregated = new Map<number, number>();
        for (const line of lines) {
            const menuItemId = Number(line.menuItemId);
            aggregated.set(menuItemId, (aggregated.get(menuItemId) ?? 0) + Number(line.quantity));
        }

        setCreating(true);
        setCreateError(null);
        try {
            await createOrder({
                restaurant_id: restaurantId.trim(),
                table_id: tableId.trim() ? Number(tableId) : null,
                notes: notes.trim() || null,
                items: Array.from(aggregated.entries()).map(([menu_item_id, quantity]) => ({
                    menu_item_id,
                    quantity,
                })),
            });
            await mutate();
            setCreateOpen(false);
        } catch (err) {
            setCreateError(err instanceof Error ? err.message : "Failed to create order.");
        } finally {
            setCreating(false);
        }
    }

    if (isLoading) {
        return (
            <div className="flex justify-center py-24">
                <Spinner size="lg" />
            </div>
        );
    }

    if (error) {
        return (
            <p className="text-sm text-red-400 text-center py-16">
                Failed to load orders. Is the order-service running?
            </p>
        );
    }

    return (
        <>
            <div className="mb-4 flex items-center justify-end">
                <Button variant="primary" onClick={openCreateModal}>
                    <Plus size={15} />
                    New Order
                </Button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 items-start">
                {COLUMNS.map((status) => {
                    const column = orders.filter((o) => o.status === status);
                    return (
                        <div key={status} className="flex flex-col gap-3">
                            <div className={clsx(
                                "flex items-center justify-between px-3 py-2.5 rounded-xl",
                                "bg-mise-surface border-t-2 border-x border-b border-mise-border",
                                COLUMN_COLORS[status],
                            )}>
                                <span className="text-xs font-semibold text-mise-text uppercase tracking-wider">
                                    {ORDER_STATUS_LABELS[status]}
                                </span>
                                <span className="text-xs font-bold text-mise-text-muted tabular-nums bg-mise-raised px-2 py-0.5 rounded-full">
                                    {column.length}
                                </span>
                            </div>

                            <div className="flex flex-col gap-3">
                                {column.length === 0 ? (
                                    <div className="text-xs text-mise-text-faint text-center py-8 border border-dashed border-mise-border rounded-xl">
                                        No orders
                                    </div>
                                ) : (
                                    column.map((order) => (
                                        <OrderCard
                                            key={order.id}
                                            order={order}
                                            onAdvance={handleAdvance}
                                            advancing={advancing === order.id}
                                        />
                                    ))
                                )}
                            </div>
                        </div>
                    );
                })}
            </div>

            <Modal isOpen={createOpen} onClose={() => setCreateOpen(false)} title="Create Order" maxWidth="max-w-2xl">
                <div className="space-y-4">
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        <Input
                            label="Restaurant Id"
                            value={restaurantId}
                            onChange={(e) => setRestaurantId(e.target.value)}
                            placeholder="restaurant-0001"
                        />
                        <Input
                            label="Table Id (optional)"
                            type="number"
                            min={1}
                            value={tableId}
                            onChange={(e) => setTableId(e.target.value)}
                            placeholder="1"
                        />
                    </div>

                    <div className="rounded-xl border border-mise-border overflow-hidden">
                        <div className="px-4 py-2.5 bg-mise-raised text-xs uppercase tracking-wider text-mise-text-muted font-semibold">
                            Order Items
                        </div>
                        <div className="p-3 space-y-2">
                            {lines.map((line) => {
                                const currentPrice = line.menuItemId !== "" ? (menuMap.get(line.menuItemId)?.price ?? 0) : 0;
                                return (
                                    <div key={line.id} className="grid grid-cols-12 gap-2 items-end">
                                        <div className="col-span-7">
                                            <label htmlFor={`menu-item-${line.id}`} className="mise-label">Menu Item</label>
                                            <select
                                                id={`menu-item-${line.id}`}
                                                className="mise-input mt-1"
                                                value={line.menuItemId}
                                                disabled={menuLoading || menuItems.length === 0}
                                                onChange={(e) => updateLine(line.id, { menuItemId: Number(e.target.value) })}
                                            >
                                                {menuItems.length === 0 ? (
                                                    <option value="">No menu items available</option>
                                                ) : (
                                                    menuItems.map((item) => (
                                                        <option key={item.id} value={item.id}>
                                                            {item.name} ({formatCurrency(item.price)})
                                                        </option>
                                                    ))
                                                )}
                                            </select>
                                        </div>
                                        <div className="col-span-2">
                                            <Input
                                                label="Qty"
                                                type="number"
                                                min={1}
                                                value={line.quantity}
                                                onChange={(e) => updateLine(line.id, { quantity: Math.max(1, Number(e.target.value || 1)) })}
                                            />
                                        </div>
                                        <div className="col-span-2 text-right text-sm text-mise-text">
                                            {formatCurrency(currentPrice * line.quantity)}
                                        </div>
                                        <div className="col-span-1">
                                            <Button
                                                variant="ghost"
                                                size="sm"
                                                onClick={() => removeLine(line.id)}
                                                disabled={lines.length <= 1}
                                                aria-label="Remove order line"
                                            >
                                                <Trash2 size={14} />
                                            </Button>
                                        </div>
                                    </div>
                                );
                            })}
                            <div className="pt-1">
                                <Button variant="secondary" size="sm" onClick={addLine}>
                                    <Plus size={14} />
                                    Add line
                                </Button>
                            </div>
                        </div>
                    </div>

                    <Input
                        label="Notes (optional)"
                        value={notes}
                        onChange={(e) => setNotes(e.target.value)}
                        placeholder="Special prep instructions..."
                    />

                    <div className="flex items-center justify-between border-t border-mise-border pt-3">
                        <p className="text-sm text-mise-text-muted">
                            Estimated total: <span className="text-mise-text font-semibold">{formatCurrency(estimatedTotal)}</span>
                        </p>
                        <div className="flex items-center gap-2">
                            <Button variant="ghost" onClick={() => setCreateOpen(false)} disabled={creating}>
                                Cancel
                            </Button>
                            <Button
                                variant="primary"
                                loading={creating}
                                onClick={handleCreateOrder}
                                disabled={menuItems.length === 0 || !restaurantId.trim()}
                            >
                                Place Order
                            </Button>
                        </div>
                    </div>
                    {createError && <p className="text-sm text-red-400">{createError}</p>}
                    {menuItems.length === 0 && (
                        <p className="text-xs text-mise-text-muted">
                            Create at least one menu item before placing orders.
                        </p>
                    )}
                </div>
            </Modal>
        </>
    );
}
