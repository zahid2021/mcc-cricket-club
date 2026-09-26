import { PublicPage } from "@/components/layout/PublicPage";

export default function SponsorsPage() {
  return (
    <PublicPage title="SPONSORS">
      <p className="text-white/60 max-w-xl mb-8">
        Partners who back the badge. Sponsorship packages and visibility are managed through the
        sponsor portal.
      </p>
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {["Title Partner", "Kit Sponsor", "Ground Partner"].map((s) => (
          <div
            key={s}
            className="rounded-sm border border-white/10 bg-white/[0.04] p-8 text-center"
          >
            <p className="font-heading text-sm uppercase tracking-[0.2em] text-mcc-gold">{s}</p>
            <p className="mt-4 text-white/30 text-xs">Logo & profile from API</p>
          </div>
        ))}
      </div>
    </PublicPage>
  );
}
