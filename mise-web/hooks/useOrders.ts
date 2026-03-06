"use client";

/**
 * SWR data hook for orders.
 *
 * Orders need frequent polling since the board must reflect kitchen updates.
 * Default interval: 5 seconds when the module is active; pauses on blur.
 */

import useSWR from "swr";
import { getOrders } from "@/lib/api/orders";
import type { Order, OrderStatus } from "@/lib/types/orders";

interface UseOrdersResult {
    orders: Order[];
    isLoading: boolean;
    error: Error | undefined;
    mutate: () => void;
}

export function useOrders(status?: OrderStatus): UseOrdersResult {
    const { data, error, isLoading, mutate } = useSWR<Order[]>(
        ["orders", status],
        () => getOrders(status),
        {
            revalidateOnFocus: true,
            refreshInterval: 5_000,
        },
    );

    return {
        orders: data ?? [],
        isLoading,
        error,
        mutate,
    };
}
