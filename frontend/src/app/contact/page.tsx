import { PublicPage } from "@/components/layout/PublicPage";

export default function ContactPage() {
  return (
    <PublicPage title="CONTACT">
      <div className="max-w-lg space-y-4 text-white/70 text-sm">
        <p>
          <span className="text-white/40 block text-xs font-heading uppercase tracking-wider mb-1">
            Club
          </span>
          Mustafa Cricket Club (MCC)
        </p>
        <p>
          <span className="text-white/40 block text-xs font-heading uppercase tracking-wider mb-1">
            Email
          </span>
          <a href="mailto:info@mustafacc.club" className="text-mcc-gold hover:text-mcc-neon">
            info@mustafacc.club
          </a>
        </p>
        <p>
          <span className="text-white/40 block text-xs font-heading uppercase tracking-wider mb-1">
            Motto
          </span>
          We Play for the Badge, Not for the Applause.
        </p>
      </div>
    </PublicPage>
  );
}
