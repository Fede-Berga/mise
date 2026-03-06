/**
 * Menu page — server component shell.
 * Delegates all interactive work to MenuPageClient.
 */

import type { Metadata } from "next";
import { PageHeader } from "@/components/layout/PageHeader";
import { MenuPageClient } from "./MenuPageClient";

export const metadata: Metadata = { title: "Menu" };

export default function MenuPage() {
    return (
        <div>
            <PageHeader
                title="Menu"
                subtitle="Manage dishes, pricing, and availability"
            />
            <MenuPageClient />
        </div>
    );
}
