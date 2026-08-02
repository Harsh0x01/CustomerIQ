import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

export default function useGsapCounter(value, formatter = (next) => Math.round(next).toLocaleString()) {
  const ref = useRef(null);

  useEffect(() => {
    if (!ref.current) {
      return undefined;
    }

    const node = ref.current;
    const counter = { value: 0 };

    const tween = gsap.to(counter, {
      value: Number(value) || 0,
      duration: 1.25,
      ease: "power3.out",
      scrollTrigger: {
        trigger: node,
        start: "top 88%",
        once: true
      },
      onUpdate: () => {
        node.textContent = formatter(counter.value);
      }
    });

    return () => {
      tween.scrollTrigger?.kill();
      tween.kill();
    };
  }, [formatter, value]);

  return ref;
}
