import Link from "next/link";

export function CtaBand() {
  return (
    <section className="relative overflow-hidden border-y border-mcc-gold/20 bg-gradient-to-r from-mcc-forest via-mcc-green/40 to-mcc-forest">
      <div className="absolute inset-0 opacity-30 bg-[radial-gradient(circle_at_30%_50%,rgba(245,197,24,0.35),transparent_50%)]" />
      <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-12 md:py-16 flex flex-col md:flex-row md:items-center md:justify-between gap-6">
        <div>
          <h2 className="font-display text-3xl sm:text-4xl tracking-wide text-white">
            WE PLAY FOR THE BADGE
          </h2>
          <p className="mt-2 text-white/70 text-sm sm:text-base max-w-lg">
            Players, captains, coaches and staff — manage selection, scoring, training and
            discipline from one secure portal.
          </p>
        </div>
        <Link
          href="/login"
          className="shrink-0 inline-flex items-center justify-center rounded-sm bg-mcc-gold px-8 py-3.5 font-heading text-sm uppercase tracking-wider text-mcc-dark hover:bg-mcc-neon transition-colors shadow-gold"
        >
          Enter Club Portal
        </Link>
      </div>
    </section>
  );
}
