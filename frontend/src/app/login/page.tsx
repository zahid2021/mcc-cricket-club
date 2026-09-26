"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const router = useRouter();
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [remember, setRemember] = useState(true);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          identifier: identifier.trim(),
          password,
          remember_me: remember,
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        setError(data.detail || data.message || "Invalid credentials");
        return;
      }
      if (typeof window !== "undefined" && data.access_token) {
        localStorage.setItem("mcc_access_token", data.access_token);
        if (data.refresh_token) {
          localStorage.setItem("mcc_refresh_token", data.refresh_token);
        }
      }
      const role = data.user?.primary_role || "player";
      if (["super_admin", "club_admin"].includes(role)) {
        router.push("/admin");
      } else if (["captain", "vice_captain", "coach", "team_manager", "scorer"].includes(role)) {
        router.push("/dashboard");
      } else if (role === "sponsor") {
        router.push("/portal/sponsor");
      } else {
        router.push("/portal/player");
      }
    } catch {
      setError("Unable to reach the server. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-mcc-dark bg-stadium-glow flex flex-col">
      <div className="flex-1 flex items-center justify-center px-4 py-16">
        <div className="w-full max-w-md">
          <div className="text-center mb-8">
            <Link href="/" className="inline-flex flex-col items-center gap-2">
              <span className="flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-br from-mcc-gold to-mcc-amber shadow-gold ring-2 ring-mcc-neon/40">
                <span className="font-display text-xl text-mcc-dark">MCC</span>
              </span>
              <span className="font-heading text-xs uppercase tracking-[0.3em] text-mcc-gold">
                Mustafa Cricket Club
              </span>
            </Link>
            <h1 className="mt-6 font-display text-4xl tracking-wide text-white">MEMBER LOGIN</h1>
            <p className="mt-2 text-sm text-white/55">Players, staff, captains & sponsors</p>
          </div>

          <form
            onSubmit={onSubmit}
            className="rounded-sm border border-white/10 bg-white/[0.04] p-6 sm:p-8 shadow-glow"
          >
            {error && (
              <div className="mb-4 rounded-sm border border-red-500/40 bg-red-500/10 px-3 py-2 text-sm text-red-200">
                {error}
              </div>
            )}
            <label className="block text-xs font-heading uppercase tracking-wider text-white/50 mb-1.5">
              Username or email
            </label>
            <input
              type="text"
              autoComplete="username"
              required
              value={identifier}
              onChange={(e) => setIdentifier(e.target.value)}
              className="w-full rounded-sm border border-white/15 bg-black/40 px-3 py-2.5 text-sm text-white outline-none focus:border-mcc-gold"
              placeholder="you@club.com"
            />
            <label className="block text-xs font-heading uppercase tracking-wider text-white/50 mt-4 mb-1.5">
              Password
            </label>
            <input
              type="password"
              autoComplete="current-password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded-sm border border-white/15 bg-black/40 px-3 py-2.5 text-sm text-white outline-none focus:border-mcc-gold"
              placeholder="••••••••"
            />
            <div className="mt-4 flex items-center justify-between gap-3 text-sm">
              <label className="flex items-center gap-2 text-white/60 cursor-pointer">
                <input
                  type="checkbox"
                  checked={remember}
                  onChange={(e) => setRemember(e.target.checked)}
                  className="accent-mcc-gold"
                />
                Remember session
              </label>
              <Link href="/forgot-password" className="text-mcc-gold hover:text-mcc-neon text-xs">
                Forgot password?
              </Link>
            </div>
            <button
              type="submit"
              disabled={loading}
              className="mt-6 w-full rounded-sm bg-mcc-gold py-3 font-heading text-sm uppercase tracking-wider text-mcc-dark hover:bg-mcc-neon disabled:opacity-60 transition-colors"
            >
              {loading ? "Signing in…" : "Sign in"}
            </button>
          </form>
          <p className="mt-6 text-center text-xs text-white/40">
            <Link href="/" className="hover:text-mcc-gold">
              ← Back to public site
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
