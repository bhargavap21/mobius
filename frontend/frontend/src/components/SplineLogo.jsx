"use client";

export default function SplineLogo({
  src = "https://my.spline.design/mobiusmiamisunset-ArOELRR7PU5HgXYf0VhmkKmZ/",
  className = "",
  height = 520,
  ariaLabel = "Interactive Mobius logo",
}) {
  const style = typeof height === "number" ? { height: `${height}px` } : { height };

  return (
    <div
      className={`relative mx-auto w-full max-w-6xl overflow-hidden rounded-2xl bg-transparent md:aspect-[16/9] aspect-[4/3] ${className}`}
      style={style}
    >
      <iframe
        src={src}
        title={ariaLabel}
        className="spline-embed absolute inset-0 h-full w-full border-0"
        loading="lazy"
        allow="fullscreen"
        referrerPolicy="no-referrer"
      />
      <noscript>
        <div className="grid h-full place-items-center text-sm text-white/60">
          Enable JavaScript to view the interactive logo.
        </div>
      </noscript>
    </div>
  );
}
