import { PublicPage } from "@/components/layout/PublicPage";

export default function MatchesPage() {
  return (
    <PublicPage title="MATCHES">
      <div className="space-y-4 max-w-2xl">
        <article className="rounded-sm border border-white/10 bg-white/[0.04] p-5">
          <span className="badge badge-selected">Upcoming</span>
          <h2 className="mt-3 font-heading text-lg text-white">MCC 1st XI vs City United CC</h2>
          <p className="mt-1 text-sm text-white/50">Sat · 2:00 PM · Central Ground · T20</p>
        </article>
        <article className="rounded-sm border border-white/10 bg-white/[0.04] p-5">
          <span className="badge badge-active">Completed</span>
          <h2 className="mt-3 font-heading text-lg text-white">MCC 1st XI vs Riverside XI</h2>
          <p className="mt-1 text-sm text-mcc-neon">MCC 168/7 · Riverside 159/9 · Won by 9 runs</p>
        </article>
      </div>
    </PublicPage>
  );
}
