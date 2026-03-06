"use client";

/**
 * SWR data hook for kitchen tickets.
 *
 * Kitchen display needs aggressive polling (10s) because ticket status changes
 * are driven by the kitchen team, not the UI user.
 */

import useSWR from "swr";
import { getTickets } from "@/lib/api/kitchen";
import type { KitchenTicket, TicketStatus } from "@/lib/types/kitchen";

interface UseKitchenTicketsResult {
    tickets: KitchenTicket[];
    isLoading: boolean;
    error: Error | undefined;
    mutate: () => void;
}

export function useKitchenTickets(status?: TicketStatus): UseKitchenTicketsResult {
    const { data, error, isLoading, mutate } = useSWR<KitchenTicket[]>(
        ["kitchen-tickets", status],
        () => getTickets(status),
        {
            revalidateOnFocus: true,
            refreshInterval: 10_000,
        },
    );

    return {
        tickets: data ?? [],
        isLoading,
        error,
        mutate,
    };
}
