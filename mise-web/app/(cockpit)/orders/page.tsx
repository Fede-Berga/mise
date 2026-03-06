/**
 * Orders page — server component shell.
 */

import type { Metadata } from "next";
import { PageHeader } from "@/components/layout/PageHeader";
import { OrdersPageClient } from "./OrdersPageClient";

export const metadata: Metadata = { title: "Orders" };

export default function OrdersPage() {
    return (
        <div>
            <PageHeader
                title="Orders"
                subtitle="Live order board — updates every 5 seconds"
            />
            <OrdersPageClient />
        </div>
    );
}
