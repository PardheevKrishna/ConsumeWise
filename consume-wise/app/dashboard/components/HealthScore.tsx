// app/dashboard/components/HealthScore.tsx
"use client";

import React from "react";
import classNames from "classnames";

interface HealthScoreProps {
  score: number;
}

const HealthScore: React.FC<HealthScoreProps> = ({ score }) => {
  const getColor = () => {
    if (score > 80) return "green";
    if (score > 50) return "orange";
    return "red";
  };

  const color = getColor();

  return (
    <div className="p-4 bg-white rounded shadow">
      <h2 className="text-xl font-semibold mb-2">Health Score</h2>
      <div className="flex items-center">
        <div
          className={classNames(
            "w-24 h-24 rounded-full border-4 flex items-center justify-center",
            {
              "border-green-500": color === "green",
              "border-orange-500": color === "orange",
              "border-red-500": color === "red",
            }
          )}
        >
          <span
            className={classNames("text-3xl font-bold", {
              "text-green-500": color === "green",
              "text-orange-500": color === "orange",
              "text-red-500": color === "red",
            })}
          >
            {score}/100
          </span>
        </div>
        <p className="ml-4 text-lg">
          {score > 80
            ? "This product is generally healthy and well-balanced."
            : score > 50
            ? "This product is moderately healthy but has some areas of concern."
            : "This product is not healthy and contains many harmful ingredients or nutrients."}
        </p>
      </div>
    </div>
  );
};

export default HealthScore;
