import Link from "next/link";

const TEAMS = [
  {
    title: "Senior",
    items: ["1st XI", "2nd XI", "Development"],
    href: "/teams?category=senior",
    accent: "from-mcc-green/40",
  },
  {
    title: "Junior",
    items: ["U19", "U16", "U14", "U12"],
    href: "/teams?category=junior",
    accent: "from-mcc-gold/30",
  },
];

const VALUES = [
  { title: "Passion", line: "In our hearts" },
  { title: "Discipline", line: "In our game" },
  { title: "Respect", line: "For all" },
  { title: "Unity", line: "Is our strength" },
];

export function TeamsAndValues() {
  return (
    <section className="relative bg-mcc-dark bg-stadium-glow">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-14 md:py-20">
        <div className="text-center max-w-2xl mx-auto mb-12">
          <p className="font-heading text-xs uppercase tracking-[0.3em] text-mcc-neon">
            The badge
          </p>
          <h2 className="mt-2 font-display text-3xl sm:text-5xl tracking-wide text-white">
            SENIOR & JUNIOR
          </h2>
          <p className="mt-4 text-white/60 text-sm sm:text-base">
            One club. Multiple pathways. From U12 to Senior 1st XI — every player under the MCC
            crest.
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-2 mb-16">
          {TEAMS.map((t) => (
            <Link
              key={t.title}
              href={t.href}
              className={`group relative overflow-hidden rounded-sm border border-white/10 bg-gradient-to-br ${t.accent} to-transparent p-8 hover:border-mcc-neon/40 transition-all`}
            >
              <h3 className="font-display text-4xl tracking-wide text-mcc-gold group-hover:text-mcc-neon transition-colors">
                {t.title.toUpperCase()}
              </h3>
              <ul className="mt-6 flex flex-wrap gap-2">
                {t.items.map((item) => (
                  <li
                    key={item}
                    className="rounded-sm border border-white/15 bg-black/30 px-3 py-1.5 text-xs font-heading uppercase tracking-wider text-white/80"
                  >
                    {item}
                  </li>
                ))}
              </ul>
              <p className="mt-6 text-sm text-mcc-gold/80 group-hover:text-mcc-gold font-heading uppercase tracking-wider">
                Explore squads →
              </p>
            </Link>
          ))}
        </div>

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {VALUES.map((v) => (
            <div
              key={v.title}
              className="text-center rounded-sm border border-white/10 bg-white/[0.03] px-4 py-6"
            >
              <p className="font-heading text-sm uppercase tracking-[0.2em] text-mcc-gold">
                {v.title}
              </p>
              <p className="mt-1 text-xs text-white/50 uppercase tracking-wider">{v.line}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
