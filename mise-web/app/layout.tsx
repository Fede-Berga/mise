/**
 * Root layout — applied to every page.
 *
 * Responsibilities:
 * - HTML metadata (SEO, OG tags)
 * - Google Fonts import via globals.css
 * - Tailwind globals injection
 * - SWR global configuration provider
 */

import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "./Providers";

export const metadata: Metadata = {
  title: { template: "%s · mise", default: "mise — Everything in its place" },
  description: "mise is a restaurant OS that keeps every part of your operation in sync.",
  openGraph: {
    title: "mise",
    description: "Restaurant OS — Everything in its place.",
    siteName: "mise",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="h-full">
      <body className="h-full bg-mise-bg text-mise-text antialiased">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
