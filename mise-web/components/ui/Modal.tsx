/**
 * Modal — accessible dialog overlay.
 *
 * Uses HTML <dialog> semantics with Tailwind for styling.
 * Closes on backdrop click and Escape key.
 */

"use client";

import { useEffect, useRef, type ReactNode } from "react";
import { clsx } from "clsx";
import { X } from "lucide-react";

interface ModalProps {
    isOpen: boolean;
    onClose: () => void;
    title: string;
    children: ReactNode;
    /** Max width class, defaults to max-w-lg */
    maxWidth?: string;
}

/**
 * @example
 * <Modal isOpen={show} onClose={() => setShow(false)} title="Add Menu Item">
 *   <MenuItemForm onSubmit={…} />
 * </Modal>
 */
export function Modal({ isOpen, onClose, title, children, maxWidth = "max-w-lg" }: ModalProps) {
    const dialogRef = useRef<HTMLDialogElement>(null);

    // Sync open state with the native dialog element
    useEffect(() => {
        const dialog = dialogRef.current;
        if (!dialog) return;
        if (isOpen && !dialog.open) dialog.showModal();
        if (!isOpen && dialog.open) dialog.close();
    }, [isOpen]);

    // Listen for native close (Escape key)
    useEffect(() => {
        const dialog = dialogRef.current;
        if (!dialog) return;
        const handleClose = () => onClose();
        dialog.addEventListener("close", handleClose);
        return () => dialog.removeEventListener("close", handleClose);
    }, [onClose]);

    return (
        <dialog
            ref={dialogRef}
            // Backdrop click closes the dialog
            onClick={(e) => e.target === dialogRef.current && onClose()}
            className={clsx(
                "bg-transparent backdrop:bg-neutral-950/80 backdrop:backdrop-blur-sm",
                "open:flex open:items-center open:justify-center w-full h-full p-4",
            )}
        >
            <div
                className={clsx(
                    "bg-mise-surface border border-mise-border rounded-2xl shadow-2xl",
                    "w-full animate-fade-in",
                    maxWidth,
                )}
                onClick={(e) => e.stopPropagation()}
            >
                {/* Header */}
                <div className="flex items-center justify-between px-6 py-4 border-b border-mise-border">
                    <h2 className="text-base font-semibold text-mise-text">{title}</h2>
                    <button
                        onClick={onClose}
                        aria-label="Close modal"
                        className="text-mise-text-muted hover:text-mise-text transition-colors rounded-lg p-1 hover:bg-mise-raised"
                    >
                        <X size={18} />
                    </button>
                </div>
                {/* Body */}
                <div className="px-6 py-5">{children}</div>
            </div>
        </dialog>
    );
}
