"use client";

import { useEffect } from 'react';

export default function SplineLogo({
  src = "https://my.spline.design/mobiusmiamisunsetcopy-MUm2jAuBTZuFMA3QOb3Rzp1a/",
  className = "",
  height = 520,
  ariaLabel = "Interactive Mobius logo",
}) {
  const style = typeof height === "number" ? { height: `${height}px` } : { height };

  useEffect(() => {
    // Remove Spline logo watermark
    const interval = setInterval(() => {
      // Try to find the iframe
      const iframe = document.querySelector('iframe.spline-embed');
      if (iframe && iframe.contentWindow) {
        try {
          // Try to access the iframe content and find spline-viewer
          const iframeDoc = iframe.contentWindow.document;
          const viewer = iframeDoc.querySelector('spline-viewer');
          if (viewer && viewer.shadowRoot) {
            const logo = viewer.shadowRoot.querySelector('#logo');
            if (logo) {
              logo.remove(); // 💥 remove the logo element entirely
              console.log("Spline logo removed!");
              clearInterval(interval);
            }
          }
        } catch (e) {
          // Cross-origin restriction - try alternative method
          // Hide the logo with CSS injection via iframe postMessage or styling
          console.log("Cross-origin restriction, trying CSS method");
        }
      }

      // Also try direct spline-viewer query (if it's not in iframe)
      const viewer = document.querySelector('spline-viewer');
      if (viewer && viewer.shadowRoot) {
        const logo = viewer.shadowRoot.querySelector('#logo');
        if (logo) {
          logo.remove(); // 💥 remove the logo element entirely
          console.log("Spline logo removed!");
          clearInterval(interval);
        }
      }
    }, 500);

    // Cleanup interval on unmount
    return () => clearInterval(interval);
  }, []);

  return (
    <div
      className={`relative mx-auto w-full max-w-6xl overflow-hidden rounded-2xl bg-transparent md:aspect-[16/9] aspect-[4/3] ${className}`}
      style={{ ...style, willChange: 'transform', transform: 'translateZ(0)' }}
    >
      <iframe
        src={src}
        title={ariaLabel}
        className="spline-embed absolute inset-0 border-0"
        width="100%"
        height="100%"
        frameBorder="0"
        loading="lazy"
        allow="fullscreen"
        referrerPolicy="no-referrer"
        style={{ pointerEvents: 'auto', willChange: 'transform', transform: 'translateZ(0)' }}
      />
      {/* Overlay to hide Spline logo */}
      <div
        className="absolute bottom-0 right-0 w-64 h-20 pointer-events-none z-10"
        style={{ background: '#000000' }}
      />
      <noscript>
        <div className="grid h-full place-items-center text-sm text-white/60">
          Enable JavaScript to view the interactive logo.
        </div>
      </noscript>
    </div>
  );
}
