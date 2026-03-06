/**
 * Currency formatting utilities.
 * Centralised here so that locale/currency changes are a single-file update.
 */

/**
 * Format a numeric amount as a localised currency string.
 *
 * @param amount   - Numeric value (e.g. 12.5)
 * @param currency - ISO 4217 currency code (e.g. "EUR", "USD")
 * @param locale   - BCP 47 locale string (e.g. "it-IT", "en-US")
 * @returns        Formatted string, e.g. "€12,50" or "$12.50"
 *
 * @example
 * formatCurrency(12.5, "EUR", "it-IT") // → "12,50 €"
 */
export function formatCurrency(
    amount: number,
    currency = "EUR",
    locale = "en-IE",
): string {
    return new Intl.NumberFormat(locale, {
        style: "currency",
        currency,
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    }).format(amount);
}
