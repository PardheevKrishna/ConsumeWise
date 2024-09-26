// app/dashboard/components/NutrientAnalysis.tsx
import React from "react";

const NutrientAnalysis = () => {
  // Placeholder data
  const macronutrients = {
    Carbohydrates: {
      Good: ["Whole grains - Rich in fiber and nutrients"],
      Bad: ["Added sugars - Increase calorie intake without nutrients"],
    },
    Proteins: {
      Good: ["Lean meats - High-quality proteins"],
      Bad: ["Processed meats - Linked to health risks"],
    },
    Fats: {
      Good: ["Omega-3 fatty acids - Beneficial for heart health"],
      Bad: ["Trans fats - Increase bad cholesterol levels"],
    },
    Fiber: {
      Good: ["Soluble fiber - Helps regulate blood sugar levels"],
    },
  };

  const micronutrients = {
    Vitamins: {
      Good: ["Vitamin D - Supports bone health"],
      Deficient: ["Vitamin B12 - Important for nerve function"],
    },
    Minerals: {
      Good: ["Calcium - Essential for bones and teeth"],
      Deficient: ["Iron - Crucial for blood health"],
    },
  };

  const healthRisks = [
    "Overconsumption of added sugars can lead to obesity and diabetes.",
    "High trans fat intake is associated with increased risk of heart disease.",
  ];

  const healthBenefits = [
    "High fiber content aids in digestion and promotes satiety.",
    "Omega-3 fatty acids support cardiovascular health.",
  ];

  return (
    <div className="p-4 bg-white rounded shadow">
      <h2 className="text-xl font-semibold mb-4">Nutritional Analysis</h2>

      {/* Macronutrients */}
      <div className="mb-4">
        <h3 className="text-lg font-semibold">Macronutrients</h3>
        {Object.entries(macronutrients).map(([key, value]) => (
          <div key={key} className="mt-2">
            <h4 className="font-medium">{key}:</h4>
            {value.Good && (
              <p className="text-green-600">
                <strong>Good:</strong> {value.Good.join(", ")}
              </p>
            )}
            {"Bad" in value && value.Bad && (
              <p className="text-red-600">
                <strong>Bad:</strong> {value.Bad.join(", ")}
              </p>
            )}
          </div>
        ))}
      </div>

      {/* Micronutrients */}
      <div className="mb-4">
        <h3 className="text-lg font-semibold">Micronutrients</h3>
        {Object.entries(micronutrients).map(([key, value]) => (
          <div key={key} className="mt-2">
            <h4 className="font-medium">{key}:</h4>
            {value.Good && (
              <p className="text-green-600">
                <strong>Good:</strong> {value.Good.join(", ")}
              </p>
            )}
            {value.Deficient && (
              <p className="text-red-600">
                <strong>Deficient:</strong> {value.Deficient.join(", ")}
              </p>
            )}
          </div>
        ))}
      </div>

      {/* Health Risks */}
      <div className="mb-4">
        <h3 className="text-lg font-semibold">Health Risks</h3>
        <ul className="list-disc list-inside text-red-600">
          {healthRisks.map((risk, index) => (
            <li key={index}>{risk}</li>
          ))}
        </ul>
      </div>

      {/* Health Benefits */}
      <div>
        <h3 className="text-lg font-semibold">Health Benefits</h3>
        <ul className="list-disc list-inside text-green-600">
          {healthBenefits.map((benefit, index) => (
            <li key={index}>{benefit}</li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default NutrientAnalysis;
