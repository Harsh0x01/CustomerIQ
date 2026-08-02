import { Canvas, useFrame } from "@react-three/fiber";
import { Preload } from "@react-three/drei";
import { useMemo, useRef } from "react";
import * as THREE from "three";

const palette = ["#00d4ff", "#7c3aed", "#22c55e", "#f59e0b"];

function seededRandom(seed) {
  let value = seed;
  return () => {
    value = (value * 9301 + 49297) % 233280;
    return value / 233280;
  };
}

function buildGraph(mode) {
  const isHero = mode === "hero";
  const count = isHero ? 96 : 56;
  const rand = seededRandom(isHero ? 42 : 19);
  const nodes = [];
  const nodeColors = [];
  const radius = isHero ? 5.8 : 6.8;

  for (let index = 0; index < count; index += 1) {
    const theta = rand() * Math.PI * 2;
    const phi = Math.acos(rand() * 2 - 1);
    const shell = radius * (0.52 + rand() * 0.48);
    const x = shell * Math.sin(phi) * Math.cos(theta);
    const y = shell * Math.sin(phi) * Math.sin(theta) * 0.72;
    const z = shell * Math.cos(phi) * 0.72;
    const color = new THREE.Color(palette[index % palette.length]);

    nodes.push([x, y, z]);
    nodeColors.push(color.r, color.g, color.b);
  }

  const edges = [];
  const edgeColors = [];
  const threshold = isHero ? 2.1 : 1.65;
  const maxEdges = isHero ? 178 : 72;

  for (let a = 0; a < nodes.length; a += 1) {
    for (let b = a + 1; b < nodes.length; b += 1) {
      if (edges.length / 6 > maxEdges) {
        break;
      }

      const distance = Math.hypot(
        nodes[a][0] - nodes[b][0],
        nodes[a][1] - nodes[b][1],
        nodes[a][2] - nodes[b][2]
      );

      if (distance < threshold && rand() > 0.18) {
        edges.push(...nodes[a], ...nodes[b]);
        const colorA = new THREE.Color(palette[a % palette.length]);
        const colorB = new THREE.Color(palette[b % palette.length]);
        edgeColors.push(colorA.r, colorA.g, colorA.b, colorB.r, colorB.g, colorB.b);
      }
    }
  }

  return {
    positions: new Float32Array(nodes.flat()),
    colors: new Float32Array(nodeColors),
    linePositions: new Float32Array(edges),
    lineColors: new Float32Array(edgeColors)
  };
}

function NetworkMesh({ mode }) {
  const group = useRef(null);
  const points = useRef(null);
  const graph = useMemo(() => buildGraph(mode), [mode]);
  const isHero = mode === "hero";

  useFrame(({ clock }) => {
    const elapsed = clock.getElapsedTime();

    if (group.current) {
      group.current.rotation.y = elapsed * (isHero ? 0.035 : 0.018);
      group.current.rotation.x = Math.sin(elapsed * 0.16) * 0.08;
    }

    if (points.current?.material) {
      points.current.material.size = (isHero ? 0.075 : 0.045) + Math.sin(elapsed * 1.4) * 0.006;
    }
  });

  return (
    <group ref={group} position={[0, isHero ? 0.15 : -0.15, isHero ? 0 : -1]}>
      <lineSegments>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            args={[graph.linePositions, 3]}
          />
          <bufferAttribute attach="attributes-color" args={[graph.lineColors, 3]} />
        </bufferGeometry>
        <lineBasicMaterial
          vertexColors
          transparent
          opacity={isHero ? 0.34 : 0.16}
          depthWrite={false}
          blending={THREE.AdditiveBlending}
        />
      </lineSegments>
      <points ref={points}>
        <bufferGeometry>
          <bufferAttribute attach="attributes-position" args={[graph.positions, 3]} />
          <bufferAttribute attach="attributes-color" args={[graph.colors, 3]} />
        </bufferGeometry>
        <pointsMaterial
          vertexColors
          transparent
          opacity={isHero ? 0.9 : 0.46}
          size={isHero ? 0.075 : 0.045}
          sizeAttenuation
          depthWrite={false}
          blending={THREE.AdditiveBlending}
        />
      </points>
    </group>
  );
}

export default function ParticleNetwork({ mode = "ambient" }) {
  const isHero = mode === "hero";

  return (
    <div className="pointer-events-none fixed inset-0 z-0" aria-hidden="true">
      <Canvas
        camera={{ position: [0, 0, isHero ? 10 : 12], fov: isHero ? 62 : 54 }}
        dpr={[1, 1.75]}
        gl={{
          antialias: true,
          alpha: true,
          powerPreference: "high-performance"
        }}
      >
        <color attach="background" args={["#0a0a0f"]} />
        <fog attach="fog" args={["#0a0a0f", 8, 18]} />
        <NetworkMesh mode={mode} />
        <Preload all />
      </Canvas>
      <div className="absolute inset-0 bg-[linear-gradient(180deg,rgba(10,10,15,0.12),#0a0a0f_86%),linear-gradient(90deg,rgba(0,212,255,0.08),transparent_38%,rgba(124,58,237,0.08))]" />
      <div className="terminal-grid absolute inset-0 opacity-[0.18]" />
    </div>
  );
}
