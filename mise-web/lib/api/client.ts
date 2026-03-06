/**
 * Base API client for the Mise Cockpit.
 *
 * All service-specific clients (menu.ts, orders.ts, kitchen.ts) call through
 * this module. It handles:
 *   - Base URL resolution from env vars
 *   - Tenant ID injection (X-Tenant-Id header)
 *   - JSON serialisation / deserialisation
 *   - Typed error normalisation
 *
 * Extending: to add a new service client, create lib/api/<service>.ts and
 * import `apiFetch` from here.
 */

/** Shape of an API error response from any Mise service. */
export class ApiError extends Error {
    constructor(
        public readonly status: number,
        message: string,
        public readonly detail?: unknown,
    ) {
        super(message);
        this.name = "ApiError";
    }
}

/** Options passed to apiFetch, extending standard RequestInit. */
export interface ApiFetchOptions extends Omit<RequestInit, "body"> {
    /** JSON body — will be serialised automatically. */
    body?: unknown;
}

/**
 * Typed fetch wrapper used by all Mise API client modules.
 *
 * @param path    - Relative path from the Next.js API proxy, e.g. "/api/menus/..."
 * @param options - Standard fetch options; pass `body` as a plain object
 * @returns       Parsed JSON response cast to T
 * @throws        ApiError on non-2xx responses
 */
export async function apiFetch<T>(
    path: string,
    options: ApiFetchOptions = {},
): Promise<T> {
    const { body, headers: extraHeaders, ...rest } = options;

    const headers: HeadersInit = {
        "Content-Type": "application/json",
        // Tenant ID: sourced from env, injected into every request.
        // In production Traefik handles this after JWT validation.
        "X-Tenant-Id": process.env.NEXT_PUBLIC_TENANT_ID ?? "restaurant-0001",
        ...extraHeaders,
    };

    const response = await fetch(path, {
        ...rest,
        headers,
        body: body !== undefined ? JSON.stringify(body) : undefined,
    });

    // Parse response regardless of status so we can include detail in errors
    const data = response.headers.get("content-type")?.includes("application/json")
        ? await response.json()
        : await response.text();

    if (!response.ok) {
        const message =
            typeof data === "object" && data !== null && "detail" in data
                ? String((data as { detail: unknown }).detail)
                : `HTTP ${response.status}`;
        throw new ApiError(response.status, message, data);
    }

    return data as T;
}
