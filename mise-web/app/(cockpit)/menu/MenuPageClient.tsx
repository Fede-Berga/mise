/**
 * MenuPageClient — fully interactive menu management view.
 *
 * Features:
 * - Item grid with category filter tabs
 * - Add item button → create modal
 * - Edit/delete actions on each card
 * - Optimistic SWR mutation after every write
 */

"use client";

import { useState } from "react";
import { useMenuItems } from "@/hooks/useMenuItems";
import { createMenuItem, updateMenuItem, deleteMenuItem } from "@/lib/api/menu";
import { MenuItemCard } from "@/components/domain/menu/MenuItemCard";
import { MenuItemForm } from "@/components/domain/menu/MenuItemForm";
import { Modal } from "@/components/ui/Modal";
import { Button } from "@/components/ui/Button";
import { Spinner } from "@/components/ui/Spinner";
import type { MenuItem, MenuItemCreate, MenuItemUpdate } from "@/lib/types/menu";
import { Plus, Search } from "lucide-react";
import { clsx } from "clsx";
import { useSession } from "next-auth/react";
import { canEditMenu } from "@/lib/auth/roles";
import type { MiseRole } from "@/lib/auth/types";

const ALL_LABEL = "All";

export function MenuPageClient() {
    const { items, isLoading, error, mutate } = useMenuItems();
    const { data: session, status } = useSession();
    const role = session?.user?.role as MiseRole | undefined;
    const canEdit = role ? canEditMenu(role) : false;

    // ── Modal state ────────────────────────────────────────────────────────────
    const [modalOpen, setModalOpen] = useState(false);
    const [editing, setEditing] = useState<MenuItem | undefined>();
    const [saving, setSaving] = useState(false);

    // ── Category filter ────────────────────────────────────────────────────────
    const [activeCategory, setActiveCategory] = useState<string>(ALL_LABEL);
    const [search, setSearch] = useState("");

    // Derive category list from items
    const categories = [ALL_LABEL, ...Array.from(new Set(items.map((i) => i.category))).sort()];

    const displayed = items.filter((item) => {
        const matchCat = activeCategory === ALL_LABEL || item.category === activeCategory;
        const matchSearch = !search || item.name.toLowerCase().includes(search.toLowerCase());
        return matchCat && matchSearch;
    });

    // ── Handlers ───────────────────────────────────────────────────────────────

    function openCreate() {
        setEditing(undefined);
        setModalOpen(true);
    }

    function openEdit(item: MenuItem) {
        setEditing(item);
        setModalOpen(true);
    }

    function closeModal() {
        setModalOpen(false);
        setEditing(undefined);
    }

    async function handleSubmit(data: MenuItemCreate | MenuItemUpdate) {
        setSaving(true);
        try {
            if (editing) {
                await updateMenuItem(editing.id, data as MenuItemUpdate);
            } else {
                await createMenuItem(data as MenuItemCreate);
            }
            await mutate();
            closeModal();
        } finally {
            setSaving(false);
        }
    }

    async function handleDelete(item: MenuItem) {
        if (!confirm(`Delete "${item.name}"? This cannot be undone.`)) return;
        await deleteMenuItem(item.id);
        await mutate();
    }

    // ── Render ─────────────────────────────────────────────────────────────────

    return (
        <div className="flex flex-col gap-5">
            {/* ── Toolbar ──────────────────────────────────────────────────── */}
            <div className="flex flex-wrap items-center gap-3">
                {/* Search */}
                <div className="relative flex-1 min-w-48 max-w-xs">
                    <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-mise-text-faint" />
                    <input
                        type="search"
                        placeholder="Search items…"
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        className="mise-input pl-8"
                    />
                </div>

                {/* Category tabs */}
                <div className="flex gap-1 flex-wrap">
                    {categories.map((cat) => (
                        <button
                            key={cat}
                            onClick={() => setActiveCategory(cat)}
                            className={clsx(
                                "px-3 py-1.5 rounded-lg text-xs font-medium transition-colors",
                                activeCategory === cat
                                    ? "bg-mise-amber text-neutral-950"
                                    : "bg-mise-raised text-mise-text-muted hover:text-mise-text",
                            )}
                        >
                            {cat}
                        </button>
                    ))}
                </div>

                {canEdit && (
                    <Button variant="primary" size="sm" onClick={openCreate} className="ml-auto">
                        <Plus size={15} />
                        Add item
                    </Button>
                )}
            </div>

            {/* ── States ───────────────────────────────────────────────────── */}
            {isLoading && (
                <div className="flex justify-center py-20">
                    <Spinner size="lg" />
                </div>
            )}
            {error && (
                <p className="text-sm text-red-400 text-center py-10">
                    Failed to load menu items. Is the menu-service running?
                </p>
            )}

            {/* ── Grid ─────────────────────────────────────────────────────── */}
            {!isLoading && displayed.length === 0 && (
                <p className="text-sm text-mise-text-muted text-center py-16">
                    {search ? `No items match "${search}".` : "No items in this category yet."}
                </p>
            )}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {displayed.map((item) => (
                    <MenuItemCard
                        key={item.id}
                        item={item}
                        onEdit={canEdit ? openEdit : undefined}
                        onDelete={canEdit ? handleDelete : undefined}
                    />
                ))}
            </div>

            {/* ── Create / Edit modal ───────────────────────────────────────── */}
            <Modal
                isOpen={modalOpen}
                onClose={closeModal}
                title={editing ? `Edit "${editing.name}"` : "Add menu item"}
            >
                <MenuItemForm
                    initialValues={editing}
                    loading={saving}
                    onSubmit={handleSubmit}
                    onCancel={closeModal}
                />
            </Modal>
        </div>
    );
}
