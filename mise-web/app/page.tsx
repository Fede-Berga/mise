/**
 * Root redirect — send unauthenticated visitors to the dashboard.
 * In a production build this redirect would be handled in middleware.ts
 * after auth token validation.
 */

import { redirect } from "next/navigation";

export default function RootPage() {
  redirect("/dashboard");
}
