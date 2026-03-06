/**
 * PageHeader — consistent page-level heading with optional actions slot.
 *
 * @example
 * <PageHeader title="Menu" subtitle="Manage dishes and pricing">
 *   <Button variant="primary" onClick={…}>Add Item</Button>
 * </PageHeader>
 */

import { type ReactNode } from "react";

interface PageHeaderProps {
    title: string;
    subtitle?: string;
    children?: ReactNode;
}

export function PageHeader({ title, subtitle, children }: PageHeaderProps) {
    return (
        <div className="flex items-start justify-between mb-6 gap-4">
            <div>
                <h1 className="text-2xl font-semibold text-mise-text tracking-tight">{title}</h1>
                {subtitle && <p className="mt-1 text-sm text-mise-text-muted">{subtitle}</p>}
            </div>
            {children && <div className="flex items-center gap-2 shrink-0">{children}</div>}
        </div>
    );
}
