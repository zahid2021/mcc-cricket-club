"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function StaffDashboardPage() {
  const router = useRouter();
  useEffect(() => {
    const token = localStorage.getItem("mcc_access_token");
    if (!token) router.replace("/login");
  }, [router]);

  return (
    <div className="min-h-screen bg-mcc-dark p-6">
      <h1 className="font-display text-3xl text-mcc-gold">Staff / Captain Dashboard</h1>
      <p className="mt-2 text-white/60 text-sm max-w-xl">
        Team selection, availability, training and authorized discipline tools — driven by your
        role permissions from the API.
      </p>
    </div>
  );
}
