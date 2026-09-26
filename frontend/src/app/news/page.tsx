import { PublicPage } from "@/components/layout/PublicPage";

export default function NewsPage() {
  return (
    <PublicPage title="NEWS">
      <article className="max-w-2xl rounded-sm border border-white/10 bg-white/[0.04] p-6">
        <p className="text-xs font-heading uppercase tracking-wider text-mcc-gold">Club news</p>
        <h2 className="mt-2 font-heading text-xl text-white">
          Senior training moved to 5:00 PM
        </h2>
        <p className="mt-3 text-sm text-white/60 leading-relaxed">
          All senior squad members: this week&apos;s training session has been rescheduled. Check
          your player portal for attendance confirmation.
        </p>
      </article>
    </PublicPage>
  );
}
