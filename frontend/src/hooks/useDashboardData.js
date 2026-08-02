import { useEffect, useMemo, useState } from "react";
import api from "../services/api.js";
import { mockDashboardData } from "../data/mockData.js";

const canUseDemoFallback = import.meta.env.VITE_ENABLE_DEMO_FALLBACK !== "false";

function currency(value) {
  return Number(value || 0);
}

function buildTrendFromPredictions(predictions = []) {
  if (!predictions.length) {
    return mockDashboardData.trend;
  }

  const buckets = new Map();

  predictions.forEach((prediction, index) => {
    const key = prediction.created_at
      ? new Date(prediction.created_at).toLocaleString("en-US", { month: "short" })
      : `B${Math.floor(index / Math.max(1, Math.ceil(predictions.length / 8))) + 1}`;
    const probability = Number(prediction.churn_probability || prediction.probability || 0);
    const bucket = buckets.get(key) || { month: key, total: 0, score: 0 };
    bucket.total += 1;
    bucket.score += probability;
    buckets.set(key, bucket);
  });

  return Array.from(buckets.values()).map((bucket) => {
    const churn = Math.round((bucket.score / bucket.total) * 1000) / 10;
    return {
      month: bucket.month,
      churn,
      retained: Math.max(0, Math.round((100 - churn) * 10) / 10)
    };
  });
}

function buildSegments(segmentResponse, customers = []) {
  if (segmentResponse?.summary && Array.isArray(segmentResponse.summary)) {
    return segmentResponse.summary.map((segment, index) => ({
      name: segment.segment_name || segment.cluster || segment.name || `Segment ${index + 1}`,
      value: Number(segment.count || segment.size || segment.value || 0),
      color: ["#00d4ff", "#7c3aed", "#f59e0b", "#ef4444", "#22c55e"][index % 5]
    }));
  }

  if (customers.length) {
    const byProducts = customers.reduce((acc, customer) => {
      const key = `${customer.num_products || 1} product${customer.num_products === 1 ? "" : "s"}`;
      acc[key] = (acc[key] || 0) + 1;
      return acc;
    }, {});

    return Object.entries(byProducts).map(([name, value], index) => ({
      name,
      value,
      color: ["#00d4ff", "#7c3aed", "#f59e0b", "#ef4444", "#22c55e"][index % 5]
    }));
  }

  return mockDashboardData.segments;
}

function topAtRisk(predictionResponse, customers = [], shapResponse) {
  const predictions = predictionResponse?.predictions || [];
  const globalDrivers = Object.entries(shapResponse?.feature_importance || {})
    .sort((a, b) => Number(b[1]) - Number(a[1]))
    .slice(0, 3)
    .map(([key]) => key.replaceAll("_", " "));

  if (predictions.length) {
    return predictions
      .map((prediction) => ({
        customer_id: prediction.customer_id || prediction.CustomerId || prediction.id || "Unknown",
        churn_probability: Number(prediction.churn_probability || prediction.probability || 0),
        risk_level: prediction.risk_level || "Medium",
        balance: currency(prediction.balance),
        estimated_salary: currency(prediction.estimated_salary),
        drivers: prediction.drivers || globalDrivers
      }))
      .sort((a, b) => b.churn_probability - a.churn_probability)
      .slice(0, 8);
  }

  if (customers.length) {
    return customers
      .map((customer) => {
        const probability =
          (customer.exited ? 0.72 : 0.18) +
          (customer.is_active_member ? 0 : 0.18) +
          Math.min(0.1, Number(customer.balance || 0) / 1000000);

        return {
          customer_id: customer.customer_id,
          churn_probability: Math.min(0.96, probability),
          risk_level: probability > 0.7 ? "High" : probability > 0.4 ? "Medium" : "Low",
          balance: currency(customer.balance),
          estimated_salary: currency(customer.estimated_salary),
          drivers: [
            customer.is_active_member ? "Lower activity decay" : "Inactive member",
            customer.num_products <= 1 ? "Low product depth" : "Product concentration",
            customer.balance > 100000 ? "High balance exposure" : "Balance sensitivity"
          ]
        };
      })
      .sort((a, b) => b.churn_probability - a.churn_probability)
      .slice(0, 8);
  }

  return mockDashboardData.atRisk;
}

export default function useDashboardData() {
  const [state, setState] = useState({
    loading: true,
    error: null,
    data: null
  });

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setState((current) => ({ ...current, loading: true, error: null }));

      try {
        const [statsResult, customersResult, churnResult, shapResult, segmentsResult] =
          await Promise.allSettled([
            api.customers.stats(),
            api.customers.list({ limit: 1200 }),
            api.predict.churn(),
            api.predict.shap(),
            api.segments.list({ n_clusters: 4 })
          ]);

        if (cancelled) {
          return;
        }

        const stats = statsResult.status === "fulfilled" ? statsResult.value : null;
        const customers =
          customersResult.status === "fulfilled"
            ? customersResult.value?.customers || []
            : [];
        const churn = churnResult.status === "fulfilled" ? churnResult.value : null;
        const shap = shapResult.status === "fulfilled" ? shapResult.value : null;
        const segmentResponse =
          segmentsResult.status === "fulfilled" ? segmentsResult.value : null;

        if (!stats && !customers.length && !canUseDemoFallback) {
          throw statsResult.reason || new Error("Dashboard data unavailable.");
        }

        const data = {
          source: stats ? "live" : "demo",
          stats: stats || mockDashboardData.stats,
          trend: buildTrendFromPredictions(churn?.predictions || customers),
          segments: buildSegments(segmentResponse, customers),
          atRisk: topAtRisk(churn, customers, shap)
        };

        setState({ loading: false, error: null, data });
      } catch (error) {
        if (cancelled) {
          return;
        }

        if (canUseDemoFallback) {
          setState({
            loading: false,
            error,
            data: mockDashboardData
          });
          return;
        }

        setState({ loading: false, error, data: null });
      }
    }

    load();

    return () => {
      cancelled = true;
    };
  }, []);

  return useMemo(() => state, [state]);
}
