import Link from "next/link";

export function SiteFooter() {
  return (
    <footer className="border-t border-white/10 bg-mcc-night">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-12 md:py-16">
        <div className="grid gap-10 md:grid-cols-3">
          <div>
            <p className="font-display text-3xl tracking-wide text-mcc-gold">MCC</p>
            <p className="mt-1 font-heading text-sm uppercase tracking-[0.2em] text-white/70">
              Mustafa Cricket Club
            </p>
            <p className="mt-4 text-sm text-white/55 max-w-xs leading-relaxed">
              Play Hard. Stay Humble. Win Together. One Team. One Dream.
            </p>
          </div>
          <div>
            <p className="font-heading text-xs uppercase tracking-[0.2em] text-mcc-neon mb-4">
              Quick Links
            </p>
            <ul className="space-y-2 text-sm text-white/65">
              <li>
                <Link href="/teams" className="hover:text-mcc-gold">
                  Teams
                </Link>
              </li>
              <li>
                <Link href="/matches" className="hover:text-mcc-gold">
                  Fixtures & Results
                </Link>
              </li>
              <li>
                <Link href="/players" className="hover:text-mcc-gold">
                  Players
                </Link>
              </li>
              <li>
                <Link href="/gallery" className="hover:text-mcc-gold">
                  Gallery
                </Link>
              </li>
            </ul>
          </div>
          <div>
            <p className="font-heading text-xs uppercase tracking-[0.2em] text-mcc-neon mb-4">
              Portals
            </p>
            <ul className="space-y-2 text-sm text-white/65">
              <li>
                <Link href="/login" className="hover:text-mcc-gold">
                  Player / Staff Login
                </Link>
              </li>
              <li>
                <Link href="/admin" className="hover:text-mcc-gold">
                  Admin Dashboard
                </Link>
              </li>
              <li>
                <Link href="/contact" className="hover:text-mcc-gold">
                  Contact Club
                </Link>
              </li>
            </ul>
          </div>
        </div>
        <div className="mt-12 pt-6 border-t border-white/10 flex flex-col sm:flex-row gap-3 justify-between text-xs text-white/40">
          <p>© {new Date().getFullYear()} Mustafa Cricket Club. All rights reserved.</p>
          <p className="italic text-white/50">
            We Play for the Badge, Not for the Applause.
          </p>
        </div>
      </div>
    </footer>
  );
}
