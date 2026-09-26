import { PublicPage } from "@/components/layout/PublicPage";

export default function TournamentsPage() {
  return (
    <PublicPage title="TOURNAMENTS">
      <p className="text-white/60 mb-6">League tables, knockout brackets and fixtures.</p>
      <div className="overflow-x-auto rounded-sm border border-white/10">
        <table className="w-full text-sm text-left">
          <thead className="bg-white/5 font-heading uppercase tracking-wider text-xs text-mcc-gold">
            <tr>
              <th className="px-4 py-3">Pos</th>
              <th className="px-4 py-3">Team</th>
              <th className="px-4 py-3">P</th>
              <th className="px-4 py-3">W</th>
              <th className="px-4 py-3">L</th>
              <th className="px-4 py-3">Pts</th>
              <th className="px-4 py-3">NRR</th>
            </tr>
          </thead>
          <tbody className="text-white/80">
            <tr className="border-t border-white/10">
              <td className="px-4 py-3">1</td>
              <td className="px-4 py-3 text-mcc-neon">Mustafa CC</td>
              <td className="px-4 py-3">12</td>
              <td className="px-4 py-3">9</td>
              <td className="px-4 py-3">3</td>
              <td className="px-4 py-3 font-semibold">18</td>
              <td className="px-4 py-3">+1.24</td>
            </tr>
            <tr className="border-t border-white/10">
              <td className="px-4 py-3">2</td>
              <td className="px-4 py-3">City United</td>
              <td className="px-4 py-3">12</td>
              <td className="px-4 py-3">8</td>
              <td className="px-4 py-3">4</td>
              <td className="px-4 py-3 font-semibold">16</td>
              <td className="px-4 py-3">+0.86</td>
            </tr>
          </tbody>
        </table>
      </div>
    </PublicPage>
  );
}
