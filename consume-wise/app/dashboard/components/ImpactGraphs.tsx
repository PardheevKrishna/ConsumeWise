// app/dashboard/components/ImpactGraphs.tsx
"use client";

import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

const data = [
  { month: "Jan", score: 75 },
  { month: "Feb", score: 80 },
  { month: "Mar", score: 78 },
  { month: "Apr", score: 85 },
  { month: "May", score: 90 },
  { month: "Jun", score: 88 },
  { month: "Jul", score: 92 },
  { month: "Aug", score: 95 },
  { month: "Sep", score: 93 },
  { month: "Oct", score: 94 },
  { month: "Nov", score: 96 },
  { month: "Dec", score: 98 },
];

const ImpactGraphs = () => {
  return (
    <div className="p-4 bg-white rounded shadow">
      <h2 className="text-xl font-semibold mb-4">Health Impact Over Time</h2>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="month" />
          <YAxis domain={[0, 100]} />
          <Tooltip />
          <Legend />
          <Line
            type="monotone"
            dataKey="score"
            stroke="#8884d8"
            activeDot={{ r: 8 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default ImpactGraphs;
