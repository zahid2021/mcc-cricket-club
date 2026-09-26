import Link from "next/link";

function PageShell({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="pt-24 pb-16 min-h-screen bg-mcc-dark bg-stadium-glow">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <p className="font-heading text-xs uppercase tracking-[0.3em] text-mcc-neon">MCC</p>
        <h1 className="mt-2 font-display text-4xl sm:text-5xl tracking-wide text-white">{title}</h1>
        <div className="mt-8">{children}</div>
      </div>
    </div>
  );
}

export default function AboutPage() {
  return (
    <PageShell title="ABOUT THE CLUB">
      <div className="max-w-3xl space-y-6 text-white/70 leading-relaxed">
        <p>
          <strong className="text-mcc-gold">Mustafa Cricket Club (MCC)</strong> is built on one
          creed: Play Hard. Stay Humble. Win Together. From junior pathways to senior first XI,
          every player wears the badge for the team — not the applause.
        </p>
        <p>
          Passion in our hearts. Discipline in our game. Respect for all. Unity is our strength.
        </p>
        <Link href="/contact" className="inline-block text-mcc-gold hover:text-mcc-neon font-heading uppercase tracking-wider text-sm">
          Contact us →
        </Link>
      </div>
    </PageShell>
  );
}
