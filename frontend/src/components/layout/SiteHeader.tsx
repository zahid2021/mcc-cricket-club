"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { Menu, X, LogIn } from "lucide-react";
import { clsx } from "clsx";

const NAV = [
  { href: "/", label: "Home" },
  { href: "/about", label: "About" },
  { href: "/teams", label: "Teams" },
  { href: "/players", label: "Players" },
  { href: "/matches", label: "Matches" },
  { href: "/tournaments", label: "Tournaments" },
  { href: "/news", label: "News" },
  { href: "/gallery", label: "Gallery" },
  { href: "/sponsors", label: "Sponsors" },
  { href: "/contact", label: "Contact" },
];

export function SiteHeader() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  // Hide public chrome on portal routes
  if (
    pathname.startsWith("/login") ||
    pathname.startsWith("/portal") ||
    pathname.startsWith("/admin") ||
    pathname.startsWith("/dashboard")
  ) {
    return null;
  }

  return (
    <header className="fixed top-0 inset-x-0 z-50">
      <div className="absolute inset-0 bg-mcc-dark/80 backdrop-blur-md border-b border-white/10" />
      <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 md:h-18 items-center justify-between gap-4">
          <Link href="/" className="flex items-center gap-3 group shrink-0">
            <span className="relative flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-mcc-gold to-mcc-amber shadow-gold ring-2 ring-mcc-neon/40">
              <span className="font-display text-lg tracking-wider text-mcc-dark">MCC</span>
            </span>
            <span className="hidden sm:flex flex-col leading-none">
              <span className="font-heading text-sm uppercase tracking-[0.2em] text-mcc-gold group-hover:text-mcc-neon transition-colors">
                Mustafa
              </span>
              <span className="font-heading text-xs uppercase tracking-[0.15em] text-white/80">
                Cricket Club
              </span>
            </span>
          </Link>

          <nav className="hidden xl:flex items-center gap-1">
            {NAV.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={clsx(
                  "px-3 py-2 text-xs font-heading uppercase tracking-wider transition-colors rounded-sm",
                  pathname === item.href
                    ? "text-mcc-gold bg-white/5"
                    : "text-white/70 hover:text-mcc-neon hover:bg-white/5"
                )}
              >
                {item.label}
              </Link>
            ))}
          </nav>

          <div className="flex items-center gap-2">
            <Link
              href="/login"
              className="inline-flex items-center gap-1.5 rounded-sm bg-mcc-gold px-3 py-2 text-xs font-heading uppercase tracking-wider text-mcc-dark hover:bg-mcc-neon transition-colors"
            >
              <LogIn className="h-3.5 w-3.5" />
              <span className="hidden sm:inline">Member Login</span>
              <span className="sm:hidden">Login</span>
            </Link>
            <button
              type="button"
              className="xl:hidden inline-flex h-10 w-10 items-center justify-center rounded-sm border border-white/15 text-white"
              aria-label={open ? "Close menu" : "Open menu"}
              onClick={() => setOpen((v) => !v)}
            >
              {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>
          </div>
        </div>
      </div>

      {open && (
        <div className="xl:hidden relative border-t border-white/10 bg-mcc-night/95 backdrop-blur-lg">
          <nav className="mx-auto max-w-7xl px-4 py-4 grid grid-cols-2 gap-1 sm:grid-cols-3">
            {NAV.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setOpen(false)}
                className={clsx(
                  "px-3 py-3 text-sm font-heading uppercase tracking-wider rounded-sm",
                  pathname === item.href
                    ? "text-mcc-gold bg-white/10"
                    : "text-white/80 hover:bg-white/5"
                )}
              >
                {item.label}
              </Link>
            ))}
          </nav>
        </div>
      )}
    </header>
  );
}
