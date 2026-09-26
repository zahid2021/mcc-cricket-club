import { PublicPage } from "@/components/layout/PublicPage";

export default function PlayersPage() {
  return (
    <PublicPage title="PLAYERS">
      <p className="text-white/60 max-w-xl mb-8">
        Searchable player directory — profiles, roles and career stats sync from match data via the
        club management API.
      </p>
      <div className="rounded-sm border border-dashed border-white/20 p-10 text-center text-white/40 text-sm">
        Player directory loads from <code className="text-mcc-neon">/api/players</code> once the
        backend is running.
      </div>
    </PublicPage>
  );
}
