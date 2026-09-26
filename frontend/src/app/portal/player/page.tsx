"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  Bell,
  Calendar,
  Home,
  LogOut,
  User,
  Users,
  AlertTriangle,
} from "lucide-react";

type Dashboard = {
  welcome_name: string;
  role_label: string;
  team: string | null;
  status: string;
  upcoming_match: string | null;
  sections: string[];
};

const MOBILE_NAV = [
  { href: "/portal/player", icon: Home, label: "Home" },
  { href: "/portal/player#matches", icon: Calendar, label: "Matches" },
  { href: "/portal/player#team", icon: Users, label: "Team" },
  { href: "/portal/player#notifications", icon: Bell, label: "Alerts" },
  { href: "/portal/player#profile", icon: User, label: "Profile" },
];

export default function PlayerPortalPage() {
  const router = useRouter();
  const [data, setData] = useState<Dashboard | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("mcc_access_token");
    if (!token) {
      router.replace("/login");
      return;
    }
    fetch("/api/portal/player/dashboard", {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then(async (r) => {
        if (r.status === 401) {
          router.replace("/login");
          return null;
        }
        if (!r.ok) {
          const j = await r.json().catch(() => ({}));
          throw new Error(j.detail || "Failed to load dashboard");
        }
        return r.json();
      })
      .then((j) => j && setData(j))
      .catch((e) => setError(e.message));
  }, [router]);

  function logout() {
    localStorage.removeItem("mcc_access_token");
    localStorage.removeItem("mcc_refresh_token");
    router.push("/login");
  }

  const statusClass =
    data?.status === "SUSPENDED"
      ? "badge-suspended"
      : data?.status === "BANNED"
        ? "badge-banned"
        : data?.status === "INJURED"
          ? "badge-injured"
          : "badge-active";

  return (
    <div className="min-h-screen bg-mcc-dark pb-24 md:pb-8">
      <header className="sticky top-0 z-40 border-b border-white/10 bg-mcc-night/95 backdrop-blur-md">
        <div className="mx-auto max-w-5xl px-4 h-14 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="font-display text-xl text-mcc-gold">MCC</span>
            <span className="text-xs font-heading uppercase tracking-wider text-white/50 hidden sm:inline">
              Player Portal
            </span>
          </div>
          <button
            type="button"
            onClick={logout}
            className="inline-flex items-center gap-1.5 text-xs text-white/50 hover:text-mcc-gold"
          >
            <LogOut className="h-4 w-4" />
            Logout
          </button>
        </div>
      </header>

      <div className="mx-auto max-w-5xl px-4 py-6">
        {error && (
          <div className="mb-4 rounded-sm border border-red-500/40 bg-red-500/10 px-3 py-2 text-sm text-red-200">
            {error}
          </div>
        )}
        {!data && !error && (
          <p className="text-white/50 text-sm">Loading dashboard…</p>
        )}
        {data && (
          <>
            <h1 className="font-display text-3xl sm:text-4xl tracking-wide text-white">
              Welcome, {data.welcome_name}
            </h1>
            <div className="mt-4 grid gap-3 sm:grid-cols-3">
              <div className="rounded-sm border border-white/10 bg-white/[0.04] p-4">
                <p className="text-[10px] font-heading uppercase tracking-wider text-white/40">
                  Role
                </p>
                <p className="mt-1 font-heading text-mcc-gold">{data.role_label}</p>
              </div>
              <div className="rounded-sm border border-white/10 bg-white/[0.04] p-4" id="team">
                <p className="text-[10px] font-heading uppercase tracking-wider text-white/40">
                  Team
                </p>
                <p className="mt-1 font-heading text-white">{data.team || "—"}</p>
              </div>
              <div className="rounded-sm border border-white/10 bg-white/[0.04] p-4">
                <p className="text-[10px] font-heading uppercase tracking-wider text-white/40">
                  Status
                </p>
                <span className={`badge mt-2 ${statusClass}`}>{data.status}</span>
              </div>
            </div>

            {data.upcoming_match && (
              <div
                id="matches"
                className="mt-6 rounded-sm border border-mcc-gold/30 bg-gradient-to-r from-mcc-gold/10 to-transparent p-5"
              >
                <p className="text-[10px] font-heading uppercase tracking-wider text-mcc-gold">
                  Upcoming Match
                </p>
                <p className="mt-2 font-heading text-lg text-white">{data.upcoming_match}</p>
              </div>
            )}

            <div id="notifications" className="mt-8">
              <h2 className="font-heading text-sm uppercase tracking-[0.2em] text-mcc-neon mb-4">
                My Dashboard
              </h2>
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
                {data.sections.map((s) => (
                  <button
                    key={s}
                    type="button"
                    className="rounded-sm border border-white/10 bg-white/[0.04] px-3 py-4 text-left text-sm text-white/80 hover:border-mcc-gold/40 hover:text-mcc-gold transition-colors"
                  >
                    {s.includes("Warning") || s.includes("Disciplinary") ? (
                      <AlertTriangle className="h-4 w-4 text-amber-400 mb-2" />
                    ) : null}
                    {s}
                  </button>
                ))}
              </div>
            </div>

            <div id="profile" className="mt-8 text-sm text-white/40">
              <Link href="/" className="hover:text-mcc-gold">
                ← Public website
              </Link>
            </div>
          </>
        )}
      </div>

      {/* Mobile bottom nav */}
      <nav className="md:hidden fixed bottom-0 inset-x-0 z-50 border-t border-white/10 bg-mcc-night/95 backdrop-blur-md">
        <div className="grid grid-cols-5 h-16">
          {MOBILE_NAV.map((item) => (
            <a
              key={item.label}
              href={item.href}
              className="flex flex-col items-center justify-center gap-0.5 text-white/50 hover:text-mcc-gold"
            >
              <item.icon className="h-5 w-5" />
              <span className="text-[10px] font-heading uppercase tracking-wide">{item.label}</span>
            </a>
          ))}
        </div>
      </nav>
    </div>
  );
}
