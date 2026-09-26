import { PublicPage } from "@/components/layout/PublicPage";

const TEAMS = [
  { name: "Senior 1st XI", category: "Senior", players: 18, record: "8–3–1" },
  { name: "Senior 2nd XI", category: "Senior", players: 16, record: "6–5–0" },
  { name: "Development", category: "Senior", players: 14, record: "—" },
  { name: "U19", category: "Junior", players: 15, record: "5–2–1" },
  { name: "U16", category: "Junior", players: 14, record: "4–3–0" },
  { name: "U14", category: "Junior", players: 12, record: "3–4–0" },
  { name: "U12", category: "Junior", players: 12, record: "—" },
];

export default function TeamsPage() {
  return (
    <PublicPage title="TEAMS">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {TEAMS.map((t) => (
          <article
            key={t.name}
            className="rounded-sm border border-white/10 bg-white/[0.04] p-5 hover:border-mcc-gold/40 transition-colors"
          >
            <span className="badge badge-selected">{t.category}</span>
            <h2 className="mt-3 font-heading text-xl text-white">{t.name}</h2>
            <p className="mt-2 text-sm text-white/50">
              {t.players} players · Record {t.record}
            </p>
          </article>
        ))}
      </div>
    </PublicPage>
  );
}
