"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

type Me = {
  full_name: string;
  primary_role: string;
  permissions: string[];
};

export default function AdminDashboardPage() {
  const router = useRouter();
  const [me, setMe] = useState<Me | null>(null);

  useEffect(() => {
    const token = localStorage.getItem("mcc_access_token");
    if (!token) {
      router.replace("/login");
      return;
    }
    fetch("/api/auth/me", { headers: { Authorization: `Bearer ${token}` } })
      .then(async (r) => {
        if (!r.ok) {
          router.replace("/login");
          return null;
        }
        return r.json();
      })
      .then((j) => j && setMe(j));
  }, [router]);

  const cards = [
    "Total Players",
    "Senior Players",
    "Junior Players",
    "Active Players",
    "Suspended",
    "Banned",
    "Upcoming Matches",
    "Tournaments",
    "Sponsors",
    "Income",
    "Expenses",
    "Pending Actions",
  ];

  return (
    <div className="min-h-screen bg-mcc-dark">
      <header className="border-b border-white/10 bg-mcc-night px-4 h-14 flex items-center justify-between">
        <span className="font-display text-xl text-mcc-gold">MCC Admin</span>
        <Link href="/" className="text-xs text-white/40 hover:text-mcc-gold">
          Public site
        </Link>
      </header>
      <div className="mx-auto max-w-6xl px-4 py-8">
        <h1 className="font-display text-3xl text-white">
          {me ? `Welcome, ${me.full_name}` : "Admin Dashboard"}
        </h1>
        <p className="mt-1 text-sm text-white/50">
          Role: {me?.primary_role?.replace(/_/g, " ") || "…"} · Permissions enforced by API
        </p>
        <div className="mt-8 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
          {cards.map((c) => (
            <div
              key={c}
              className="rounded-sm border border-white/10 bg-white/[0.04] p-4"
            >
              <p className="text-[10px] font-heading uppercase tracking-wider text-white/40">{c}</p>
              <p className="mt-2 font-display text-2xl text-mcc-neon">—</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
