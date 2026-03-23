"use client";

import Image from "next/image";

export default function HeroPanel() {
  return (
    <section className="hero-panel overflow-hidden rounded-[30px] border border-white/10 px-5 py-4 shadow-2xl shadow-black/40 sm:px-6 lg:px-7 lg:py-4">
      <div className="relative z-10 grid gap-4 lg:grid-cols-[1.75fr_0.6fr] lg:items-center">
        <div className="space-y-2">
          <div className="inline-flex items-center gap-2 rounded-full border border-red-500/30 bg-red-500/10 px-4 py-1 text-[11px] font-medium uppercase tracking-[0.28em] text-red-100">
            Pokemon Madrid Tournament Radar
          </div>

          <div className="space-y-1.5">
            <h1 className="font-display max-w-4xl text-[1.65rem] font-semibold uppercase tracking-[0.08em] text-white sm:text-3xl lg:text-[1.95rem]">
              El calendario competitivo para la comunidad Pokemon de Madrid
            </h1>
            <p className="max-w-3xl text-sm leading-6 text-zinc-400">
              Consulta de un vistazo los eventos oficiales mas relevantes.
            </p>
          </div>
        </div>

        <div className="relative hidden items-center lg:flex">
          <div className="logo-orb absolute h-36 w-36 rounded-full blur-3xl" />
          <div className="hero-logo-wrap relative flex items-center justify-center">
            <Image
              src="/images/logo.png"
              alt="Pokemon Madrid Events"
              width={176}
              height={176}
              priority
              className="hero-logo h-auto w-auto"
            />
          </div>
        </div>
      </div>
    </section>
  );
}
