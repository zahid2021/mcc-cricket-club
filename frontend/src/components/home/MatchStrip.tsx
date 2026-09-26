import Link from "next/link";

type MatchCard = {
  id: string;
  label: string;
  home: string;
  away: string;
  meta: string;
  status: "upcoming" | "live" | "completed";
  score?: string;
};

const MATCHES: MatchCard[] = [
  {
    id: "1",
    label: "Upcoming",
    home: "Mustafa CC 1st XI",
    away: "City United CC",
    meta: "Sat · 2:00 PM · Central Ground",
    status: "upcoming",
  },
  {
    id: "2",
    label: "Latest Result",
    home: "Mustafa CC 1st XI",
    away: "Riverside XI",
    meta: "T20 · League",
    status: "completed",
    score: "MCC 168/7 · Riverside 159/9",
  },
  {
    id: "3",
    label: "Junior Fixture",
    home: "MCC U16",
    away: "Academy Stars U16",
    meta: "Sun · 9:00 AM · Academy Pitch",
    status: "upcoming",
  },
];

export function MatchStrip() {
  return (
    <section className="relative bg-mcc-night border-y border-white/10">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-12 md:py-16">
        <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4 mb-8">
          <div>
            <p className="font-heading text-xs uppercase tracking-[0.3em] text-mcc-neon">
              On the field
            </p>
            <h2 className="mt-2 font-display text-3xl sm:text-4xl tracking-wide text-white">
              MATCHES
            </h2>
          </div>
          <Link
            href="/matches"
            className="text-sm font-heading uppercase tracking-wider text-mcc-gold hover:text-mcc-neon"
          >
            All fixtures →
          </Link>
        </div>
        <div className="grid gap-4 md:grid-cols-3">
          {MATCHES.map((m) => (
            <article
              key={m.id}
              className="relative overflow-hidden rounded-sm border border-white/10 bg-gradient-to-br from-white/[0.06] to-transparent p-5 hover:border-mcc-gold/40 transition-colors"
            >
              <div className="flex items-center justify-between gap-2 mb-4">
                <span className="font-heading text-[10px] uppercase tracking-[0.2em] text-white/50">
                  {m.label}
                </span>
                {m.status === "live" && <span className="badge badge-live">Live</span>}
                {m.status === "upcoming" && (
                  <span className="badge badge-selected">Upcoming</span>
                )}
                {m.status === "completed" && (
                  <span className="badge badge-active">Completed</span>
                )}
              </div>
              <p className="font-heading text-lg text-white leading-snug">
                {m.home}
              </p>
              <p className="text-xs font-heading uppercase tracking-widest text-mcc-gold my-1">
                vs
              </p>
              <p className="font-heading text-lg text-white/90 leading-snug">{m.away}</p>
              {m.score && (
                <p className="mt-3 text-sm text-mcc-neon font-medium">{m.score}</p>
              )}
              <p className="mt-3 text-xs text-white/45">{m.meta}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
