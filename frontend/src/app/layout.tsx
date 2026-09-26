import type { Metadata, Viewport } from "next";
import { Bebas_Neue, Oswald, DM_Sans } from "next/font/google";
import "./globals.css";
import { SiteHeader } from "@/components/layout/SiteHeader";
import { SiteFooter } from "@/components/layout/SiteFooter";

const bebas = Bebas_Neue({
  weight: "400",
  subsets: ["latin"],
  variable: "--font-bebas",
  display: "swap",
});

const oswald = Oswald({
  subsets: ["latin"],
  variable: "--font-oswald",
  display: "swap",
});

const dmSans = DM_Sans({
  subsets: ["latin"],
  variable: "--font-dm-sans",
  display: "swap",
});

export const metadata: Metadata = {
  title: {
    default: "Mustafa Cricket Club | MCC",
    template: "%s | Mustafa Cricket Club",
  },
  description:
    "Mustafa Cricket Club — Play Hard. Stay Humble. Win Together. One Team. One Dream.",
  keywords: [
    "Mustafa Cricket Club",
    "MCC",
    "cricket",
    "club management",
    "Pakistan cricket",
  ],
};

export const viewport: Viewport = {
  themeColor: "#06140a",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${bebas.variable} ${oswald.variable} ${dmSans.variable}`}>
      <body className="min-h-screen flex flex-col">
        <SiteHeader />
        <main className="flex-1">{children}</main>
        <SiteFooter />
      </body>
    </html>
  );
}
