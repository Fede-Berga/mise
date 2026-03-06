/**
 * MenuItemCard — display a single menu item in the grid.
 * Clicking the card opens the edit flow (onEdit callback).
 */

import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { formatCurrency } from "@/lib/utils/currency";
import type { MenuItem } from "@/lib/types/menu";
import { Pencil, Trash2 } from "lucide-react";

interface MenuItemCardProps {
    item: MenuItem;
    onEdit?: (item: MenuItem) => void;
    onDelete?: (item: MenuItem) => void;
}

/**
 * @example
 * <MenuItemCard item={item} onEdit={setEditing} onDelete={handleDelete} />
 */
export function MenuItemCard({ item, onEdit, onDelete }: MenuItemCardProps) {
    return (
        <Card className="flex flex-col gap-3 group hover:border-mise-amber/50 transition-colors">
            {/* Header row */}
            <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold text-mise-text truncate">{item.name}</p>
                    <p className="text-xs text-mise-text-muted mt-0.5">{item.category}</p>
                </div>
                <span className="text-base font-bold text-mise-amber shrink-0">
                    {formatCurrency(item.price)}
                </span>
            </div>

            {/* Description */}
            {item.description && (
                <p className="text-xs text-mise-text-muted line-clamp-2">{item.description}</p>
            )}

            {/* Footer */}
            <div className="flex items-center justify-between mt-auto pt-2 border-t border-mise-border">
                <Badge variant={item.is_available ? "green" : "zinc"}>
                    {item.is_available ? "Available" : "Unavailable"}
                </Badge>

                {/* Action buttons — appear on hover if permitted */}
                {(onEdit || onDelete) && (
                    <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        {onEdit && (
                            <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => onEdit(item)}
                                aria-label={`Edit ${item.name}`}
                            >
                                <Pencil size={14} />
                            </Button>
                        )}
                        {onDelete && (
                            <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => onDelete(item)}
                                aria-label={`Delete ${item.name}`}
                                className="hover:text-red-400"
                            >
                                <Trash2 size={14} />
                            </Button>
                        )}
                    </div>
                )}
            </div>
        </Card>
    );
}
