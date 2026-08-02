export const mockDashboardData = {
  source: "demo",
  stats: {
    total_customers: 12480,
    churned: 1809,
    active: 10671,
    churn_rate: 14.5,
    avg_balance: 82540,
    avg_age: 41.8,
    avg_tenure: 6.2
  },
  trend: [
    { month: "Jan", churn: 12.4, retained: 87.6 },
    { month: "Feb", churn: 13.1, retained: 86.9 },
    { month: "Mar", churn: 13.8, retained: 86.2 },
    { month: "Apr", churn: 15.2, retained: 84.8 },
    { month: "May", churn: 14.7, retained: 85.3 },
    { month: "Jun", churn: 16.1, retained: 83.9 },
    { month: "Jul", churn: 15.4, retained: 84.6 },
    { month: "Aug", churn: 14.9, retained: 85.1 },
    { month: "Sep", churn: 13.6, retained: 86.4 },
    { month: "Oct", churn: 12.9, retained: 87.1 },
    { month: "Nov", churn: 13.4, retained: 86.6 },
    { month: "Dec", churn: 12.2, retained: 87.8 }
  ],
  segments: [
    { name: "Prime Loyalists", value: 34, color: "#00d4ff" },
    { name: "Balance Builders", value: 27, color: "#7c3aed" },
    { name: "Dormant High Value", value: 18, color: "#f59e0b" },
    { name: "Price Sensitive", value: 21, color: "#ef4444" }
  ],
  atRisk: [
    {
      customer_id: "CUST-90241",
      churn_probability: 0.91,
      risk_level: "High",
      balance: 154200,
      estimated_salary: 184000,
      drivers: ["Inactive member", "High balance", "Single product"]
    },
    {
      customer_id: "CUST-18402",
      churn_probability: 0.86,
      risk_level: "High",
      balance: 120450,
      estimated_salary: 132500,
      drivers: ["Low tenure", "No card", "Balance spike"]
    },
    {
      customer_id: "CUST-44119",
      churn_probability: 0.79,
      risk_level: "High",
      balance: 98210,
      estimated_salary: 111400,
      drivers: ["Inactive member", "Two complaints", "Low tenure"]
    },
    {
      customer_id: "CUST-77300",
      churn_probability: 0.72,
      risk_level: "Medium",
      balance: 64380,
      estimated_salary: 94500,
      drivers: ["Low product depth", "Salary mismatch", "Age band"]
    }
  ]
};

export const mockSegments = {
  summary: [
    { name: "Prime Loyalists", size: 4120, churnRate: 6.2, clv: 218000 },
    { name: "Balance Builders", size: 3310, churnRate: 11.4, clv: 144000 },
    { name: "Dormant High Value", size: 2240, churnRate: 28.8, clv: 186000 },
    { name: "Price Sensitive", size: 2810, churnRate: 22.1, clv: 82000 }
  ],
  points: Array.from({ length: 180 }, (_, index) => {
    const cluster = index % 4;
    const center = [
      [-2.8, 1.4, -0.8],
      [1.9, 1.1, 0.6],
      [-1.1, -1.8, 1.2],
      [2.4, -1.4, -1.1]
    ][cluster];

    return {
      id: `CUST-${String(10000 + index)}`,
      cluster,
      x: center[0] + Math.sin(index * 1.7) * 0.55,
      y: center[1] + Math.cos(index * 1.3) * 0.55,
      z: center[2] + Math.sin(index * 0.9) * 0.55
    };
  })
};
