"use client";

import Link from "next/link";

export default function ForgotPasswordPage() {
  return (
    <div className="min-h-screen bg-mcc-dark flex items-center justify-center px-4">
      <div className="max-w-md w-full text-center">
        <h1 className="font-display text-3xl text-mcc-gold">RESET PASSWORD</h1>
        <p className="mt-3 text-sm text-white/60">
          Password reset emails will be wired through the API (
          <code className="text-mcc-neon">/api/auth/forgot-password</code>). Contact your club
          admin if you need immediate access.
        </p>
        <Link href="/login" className="mt-6 inline-block text-mcc-gold hover:text-mcc-neon text-sm">
          ← Back to login
        </Link>
      </div>
    </div>
  );
}
