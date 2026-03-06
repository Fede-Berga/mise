/**
 * Kitchen page — server component shell.
 */

import type { Metadata } from "next";
import { PageHeader } from "@/components/layout/PageHeader";
import { KitchenPageClient } from "./KitchenPageClient";

export const metadata: Metadata = { title: "Kitchen" };

export default function KitchenPage() {
    return (
        <div>
            <PageHeader
                title="Kitchen Display"
                subtitle="Live ticket board — refreshes every 10 seconds"
            />
            <KitchenPageClient />
        </div>
    );
}
