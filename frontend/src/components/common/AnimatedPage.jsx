import { useLayoutEffect, useRef } from "react";
import gsap from "gsap";

export default function AnimatedPage({ routeKey, children }) {
  const scope = useRef(null);

  useLayoutEffect(() => {
    if (!scope.current) {
      return undefined;
    }

    const context = gsap.context(() => {
      gsap.fromTo(
        scope.current,
        { autoAlpha: 0, y: 16 },
        { autoAlpha: 1, y: 0, duration: 0.48, ease: "power3.out" }
      );
    }, scope);

    return () => context.revert();
  }, [routeKey]);

  return (
    <main ref={scope} className="relative z-10 min-h-screen">
      {children}
    </main>
  );
}
