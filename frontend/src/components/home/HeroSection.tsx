"use client";

import Image from "next/image";
import Link from "next/link";
import { useEffect, useState } from "react";

export function HeroSection() {
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const t = requestAnimationFrame(() => setReady(true));
    return () => cancelAnimationFrame(t);
  }, []);

  return (
    <section className="relative min-h-[100svh] w-full overflow-hidden bg-mcc-dark">
      {/* Full-bleed hero image */}
      <div className="absolute inset-0">
        <Image
          src="/images/mcc-hero.png"
          alt="Mustafa Cricket Club — Play Hard. Stay Humble. Win Together."
          fill
          priority
          sizes="100vw"
          className={`object-cover object-[center_20%] sm:object-center transition-transform duration-[1.8s] ease-out ${
            ready ? "scale-100" : "scale-110"
          }`}
        />
        {/* Gradients for readability on mobile — image already has branding */}
        <div className="absolute inset-0 bg-gradient-to-t from-mcc-dark via-mcc-dark/40 to-mcc-dark/20 sm:via-mcc-dark/25 sm:to-transparent" />
        <div className="absolute inset-0 bg-gradient-to-r from-mcc-dark/70 via-transparent to-mcc-dark/50 hidden md:block" />
      </div>

      {/* Content overlaid — brand-first, minimal hero budget */}
      <div className="relative z-10 flex min-h-[100svh] flex-col justify-end pb-16 pt-24 sm:justify-center sm:pb-0 sm:pt-20">
        <div className="mx-auto w-full max-w-7xl px-4 sm:px-6 lg:px-8">
          <div
            className={`max-w-xl transition-all duration-1000 ${
              ready ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"
            }`}
          >
            <p className="font-heading text-[10px] sm:text-xs uppercase tracking-[0.35em] text-mcc-gold drop-shadow-md">
              Play Hard · Stay Humble · Win Together
            </p>
            <h1 className="mt-3 font-display text-5xl sm:text-6xl md:text-7xl lg:text-8xl leading-[0.9] tracking-wide text-white drop-shadow-[0_4px_24px_rgba(0,0,0,0.85)]">
              <span className="text-mcc-gold">MUSTAFA</span>
              <br />
              <span className="text-white">CRICKET CLUB</span>
            </h1>
            <p className="mt-4 font-heading text-sm sm:text-base uppercase tracking-[0.25em] text-mcc-neon drop-shadow-md">
              One Team. One Dream.
            </p>
            <p className="mt-5 max-w-md text-sm sm:text-base text-white/80 leading-relaxed">
              Senior & junior cricket under one badge — fixtures, selection, live scoring,
              and the full club operations platform.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link
                href="/matches"
                className="inline-flex items-center justify-center rounded-sm bg-mcc-gold px-6 py-3 font-heading text-sm uppercase tracking-wider text-mcc-dark shadow-gold hover:bg-mcc-neon transition-colors"
              >
                View Fixtures
              </Link>
              <Link
                href="/login"
                className="inline-flex items-center justify-center rounded-sm border border-mcc-neon/60 bg-mcc-dark/50 px-6 py-3 font-heading text-sm uppercase tracking-wider text-mcc-neon backdrop-blur-sm hover:bg-mcc-neon/10 transition-colors"
              >
                Player Portal
              </Link>
            </div>
          </div>
        </div>

        {/* Scroll hint */}
        <div
          className={`absolute bottom-6 left-1/2 -translate-x-1/2 hidden sm:flex flex-col items-center gap-2 transition-opacity duration-1000 delay-700 ${
            ready ? "opacity-70" : "opacity-0"
          }`}
        >
          <span className="text-[10px] font-heading uppercase tracking-[0.3em] text-white/50">
            Scroll
          </span>
          <span className="h-8 w-px bg-gradient-to-b from-mcc-gold to-transparent animate-pulse" />
        </div>
      </div>
    </section>
  );
}
