import { useLayoutEffect, useRef } from "react";
import gsap from "gsap";

export default function usePageIntro(dependencies = []) {
  const scope = useRef(null);

  useLayoutEffect(() => {
    if (!scope.current) {
      return undefined;
    }

    const context = gsap.context(() => {
      gsap.fromTo(
        "[data-reveal]",
        { autoAlpha: 0, y: 18 },
        {
          autoAlpha: 1,
          y: 0,
          duration: 0.72,
          ease: "power3.out",
          stagger: 0.08
        }
      );
    }, scope);

    return () => context.revert();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, dependencies);

  return scope;
}
