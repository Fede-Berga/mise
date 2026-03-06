/**
 * Dashboard page — operational overview.
 *
 * Server component: renders KPI cards (static shapes) and mounts a client
 * child that fetches live data. This keeps the initial HTML fast while
 * allowing SWR polling for the live order list.
 *
 * Extending: add new KPI cards to <KpiGrid> and wire them to the relevant
 * service client in lib/api/.
 */

import type { Metadata } from "next";
import { PageHeader } from "@/components/layout/PageHeader";
import { DashboardClient } from "./DashboardClient";

export const metadata: Metadata = {
    title: "Dashboard",
};

export default function DashboardPage() {
    return (
        <div>
            <PageHeader
                title="Dashboard"
                subtitle="Real-time overview of your restaurant operations"
            />
            <DashboardClient />
        </div>
    );
}
