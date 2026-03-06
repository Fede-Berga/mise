/**
 * Cockpit layout — wraps all authenticated app pages.
 *
 * Structure:
 *   Fixed 240px sidebar | Scrollable main column
 *     Fixed 56px topbar
 *     Page content (padded)
 *
 * Extending: add auth guards here (e.g. check JWT in server-side props)
 * before rendering children.
 */

import { Sidebar } from "@/components/layout/Sidebar";
import { Topbar } from "@/components/layout/Topbar";
import { Providers } from "@/app/Providers";

export default function CockpitLayout({ children }: { children: React.ReactNode }) {
    return (
        <Providers>
            <div className="flex h-full">
                <Sidebar />
                {/* Main column — offset left by sidebar width */}
                <div className="flex flex-1 flex-col pl-60 min-h-full">
                    <Topbar />
                    <main className="flex-1 p-6 max-w-screen-2xl">
                        {children}
                    </main>
                </div>
            </div>
        </Providers>
    );
}
