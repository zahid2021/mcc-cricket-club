import Link from "next/link";

export function PublicPage({
  eyebrow = "Mustafa Cricket Club",
  title,
  children,
}: {
  eyebrow?: string;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="pt-24 pb-16 min-h-screen bg-mcc-dark bg-stadium-glow">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <p className="font-heading text-xs uppercase tracking-[0.3em] text-mcc-neon">{eyebrow}</p>
        <h1 className="mt-2 font-display text-4xl sm:text-5xl tracking-wide text-white">{title}</h1>
        <div className="mt-8">{children}</div>
        <p className="mt-12">
          <Link href="/" className="text-sm text-white/40 hover:text-mcc-gold">
            ← Home
          </Link>
        </p>
      </div>
    </div>
  );
}
