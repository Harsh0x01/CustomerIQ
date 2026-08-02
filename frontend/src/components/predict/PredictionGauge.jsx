import { useEffect, useRef } from "react";
import gsap from "gsap";

export default function PredictionGauge({ probability = 0 }) {
  const circleRef = useRef(null);
  const valueRef = useRef(null);
  const normalized = Math.min(1, Math.max(0, Number(probability || 0)));
  const circumference = 2 * Math.PI * 86;

  useEffect(() => {
    const circle = circleRef.current;
    const valueNode = valueRef.current;

    if (!circle || !valueNode) {
      return undefined;
    }

    const counter = { value: 0 };
    const timeline = gsap.timeline();
    timeline.to(circle, {
      strokeDashoffset: circumference * (1 - normalized),
      duration: 1.2,
      ease: "power3.out"
    });
    timeline.to(
      counter,
      {
        value: normalized * 100,
        duration: 1.2,
        ease: "power3.out",
        onUpdate: () => {
          valueNode.textContent = `${counter.value.toFixed(1)}%`;
        }
      },
      "<"
    );

    return () => timeline.kill();
  }, [circumference, normalized]);

  return (
    <div className="flex items-center justify-center">
      <div className="relative h-56 w-56">
        <svg viewBox="0 0 220 220" className="h-full w-full -rotate-90">
          <circle
            cx="110"
            cy="110"
            r="86"
            fill="none"
            stroke="rgba(255,255,255,0.08)"
            strokeWidth="14"
          />
          <circle
            ref={circleRef}
            cx="110"
            cy="110"
            r="86"
            fill="none"
            stroke={normalized > 0.7 ? "#ef4444" : normalized > 0.42 ? "#f59e0b" : "#00d4ff"}
            strokeLinecap="round"
            strokeWidth="14"
            strokeDasharray={circumference}
            strokeDashoffset={circumference}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span ref={valueRef} className="data-number text-4xl font-semibold text-ink">
            0.0%
          </span>
          <span className="mt-1 font-mono text-xs uppercase text-muted">Churn probability</span>
        </div>
      </div>
    </div>
  );
}
