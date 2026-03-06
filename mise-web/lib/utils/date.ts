/**
 * Date formatting utilities.
 * Uses Intl.DateTimeFormat and Intl.RelativeTimeFormat for localised output.
 */

/**
 * Format an ISO 8601 date string as a short date.
 * @example formatDate("2025-02-25T12:00:00Z") → "25 Feb 2025"
 */
export function formatDate(iso: string): string {
    return new Intl.DateTimeFormat("en-GB", {
        day: "2-digit",
        month: "short",
        year: "numeric",
    }).format(new Date(iso));
}

/**
 * Format an ISO 8601 date string as a time.
 * @example formatTime("2025-02-25T12:05:00Z") → "12:05"
 */
export function formatTime(iso: string): string {
    return new Intl.DateTimeFormat("en-GB", {
        hour: "2-digit",
        minute: "2-digit",
    }).format(new Date(iso));
}

/**
 * Return a human-readable relative time string.
 * @example formatRelative("2025-02-25T11:55:00Z") → "5 minutes ago"
 */
export function formatRelative(iso: string): string {
    const diff = (new Date(iso).getTime() - Date.now()) / 1000; // seconds (negative = past)
    const abs = Math.abs(diff);

    const rtf = new Intl.RelativeTimeFormat("en", { numeric: "auto" });

    if (abs < 60) return rtf.format(Math.round(diff), "second");
    if (abs < 3600) return rtf.format(Math.round(diff / 60), "minute");
    if (abs < 86400) return rtf.format(Math.round(diff / 3600), "hour");
    return rtf.format(Math.round(diff / 86400), "day");
}
