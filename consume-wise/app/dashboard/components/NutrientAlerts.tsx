// app/dashboard/components/NutrientAlerts.tsx
import React from "react";

interface NutrientAlertsProps {
  deficiencies: string[];
}

const NutrientAlerts: React.FC<NutrientAlertsProps> = ({
  deficiencies = ["Vitamin B12", "Iron"],
}) => {
  return (
    <div className="p-4 bg-white rounded shadow">
      <h2 className="text-xl font-semibold mb-4">Nutrient Deficiency Alerts</h2>
      {deficiencies.length > 0 ? (
        <ul className="list-disc list-inside text-red-600">
          {deficiencies.map((deficiency, index) => (
            <li key={index}>
              <strong>{deficiency}:</strong> Consider supplements or dietary
              changes to address this deficiency.
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-green-600">No nutrient deficiencies detected.</p>
      )}
    </div>
  );
};

export default NutrientAlerts;
