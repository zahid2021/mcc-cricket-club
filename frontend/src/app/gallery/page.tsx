import { PublicPage } from "@/components/layout/PublicPage";

export default function GalleryPage() {
  return (
    <PublicPage title="GALLERY">
      <p className="text-white/60 mb-6">Match days, training and club events.</p>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <div
            key={i}
            className="aspect-[4/3] rounded-sm border border-white/10 bg-gradient-to-br from-mcc-green/30 to-mcc-dark"
          />
        ))}
      </div>
    </PublicPage>
  );
}
