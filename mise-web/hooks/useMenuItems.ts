"use client";

/**
 * SWR data hook for menu items.
 *
 * Uses SWR with a 30-second revalidation interval — menu changes are
 * infrequent so we don't need aggressive polling.
 *
 * Usage:
 *   const { items, isLoading, error, mutate } = useMenuItems();
 */

import useSWR from "swr";
import { getMenuItems } from "@/lib/api/menu";
import type { MenuItem } from "@/lib/types/menu";

interface UseMenuItemsResult {
    items: MenuItem[];
    isLoading: boolean;
    error: Error | undefined;
    mutate: () => void;
}

export function useMenuItems(): UseMenuItemsResult {
    const { data, error, isLoading, mutate } = useSWR<MenuItem[]>(
        "menu-items",
        () => getMenuItems(),
        {
            revalidateOnFocus: true,
            refreshInterval: 30_000,
        },
    );

    return {
        items: data ?? [],
        isLoading,
        error,
        mutate,
    };
}
