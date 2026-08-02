import { useLocation, Routes, Route } from "react-router-dom";
import { useMemo } from "react";
import AnimatedPage from "./components/common/AnimatedPage.jsx";
import ErrorBoundary from "./components/common/ErrorBoundary.jsx";
import ParticleNetwork from "./components/three/ParticleNetwork.jsx";
import HeroPage from "./pages/HeroPage.jsx";
import DashboardPage from "./pages/DashboardPage.jsx";
import PredictPage from "./pages/PredictPage.jsx";
import SegmentsPage from "./pages/SegmentsPage.jsx";
import IntelligencePage from "./pages/IntelligencePage.jsx";

export default function App() {
  const location = useLocation();
  const isHero = location.pathname === "/";
  const canvasMode = useMemo(() => (isHero ? "hero" : "ambient"), [isHero]);

  return (
    <ErrorBoundary>
      <div className="relative min-h-screen overflow-x-hidden bg-void text-ink">
        <ParticleNetwork mode={canvasMode} />
        <AnimatedPage routeKey={location.pathname}>
          <Routes location={location}>
            <Route path="/" element={<HeroPage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/predict" element={<PredictPage />} />
            <Route path="/segments" element={<SegmentsPage />} />
            <Route path="/intelligence" element={<IntelligencePage />} />
          </Routes>
        </AnimatedPage>
      </div>
    </ErrorBoundary>
  );
}
