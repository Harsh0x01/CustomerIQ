import { Canvas } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import { useMemo } from "react";
import * as THREE from "three";

const colors = ["#00d4ff", "#7c3aed", "#f59e0b", "#ef4444", "#22c55e"];

function ScatterPoints({ points, selectedCluster, onSelectCluster }) {
  const materialCache = useMemo(
    () =>
      colors.map(
        (color) =>
          new THREE.MeshBasicMaterial({
            color,
            transparent: true,
            opacity: 0.86,
            depthWrite: false
          })
      ),
    []
  );

  return (
    <group>
      {points.map((point) => {
        const selected = selectedCluster === null || selectedCluster === point.cluster;
        return (
          <mesh
            key={point.id}
            position={[point.x, point.y, point.z]}
            scale={selected ? 1 : 0.58}
            material={materialCache[point.cluster % materialCache.length]}
            onClick={(event) => {
              event.stopPropagation();
              onSelectCluster(point.cluster);
            }}
          >
            <sphereGeometry args={[selected ? 0.055 : 0.035, 16, 16]} />
          </mesh>
        );
      })}
    </group>
  );
}

export default function SegmentScatter({ points, selectedCluster, onSelectCluster }) {
  return (
    <div className="h-[420px] overflow-hidden rounded-lg border border-white/10 bg-[#0c0d13]">
      <Canvas
        camera={{ position: [0, 0, 7.5], fov: 48 }}
        dpr={[1, 1.75]}
        gl={{ antialias: true, alpha: true }}
        onPointerMissed={() => onSelectCluster(null)}
      >
        <color attach="background" args={["#0c0d13"]} />
        <gridHelper args={[7, 14, "#1f2937", "#161b25"]} rotation={[Math.PI / 2, 0, 0]} />
        <ScatterPoints
          points={points}
          selectedCluster={selectedCluster}
          onSelectCluster={onSelectCluster}
        />
        <OrbitControls enablePan={false} minDistance={4.5} maxDistance={10} />
      </Canvas>
    </div>
  );
}
