// app/dashboard/components/AllergenAlerts.tsx
import React from "react";

interface AllergenAlertsProps {
  allergens: string[];
  crossContamination: string[];
}

const AllergenAlerts: React.FC<AllergenAlertsProps> = ({
  allergens = ["Peanuts", "Gluten"],
  crossContamination = ["Processed in a facility that handles nuts"],
}) => {
  return (
    <div className="p-4 bg-white rounded shadow">
      <h2 className="text-xl font-semibold mb-4">Allergen Alerts</h2>

      {/* Allergen List */}
      <div className="mb-4">
        <h3 className="text-lg font-medium">Detected Allergens:</h3>
        {allergens.length > 0 ? (
          <ul className="list-disc list-inside text-red-600">
            {allergens.map((allergen, index) => (
              <li key={index}>{allergen}</li>
            ))}
          </ul>
        ) : (
          <p className="text-green-600">No allergens detected.</p>
        )}
      </div>

      {/* Cross-Contamination Risks */}
      <div>
        <h3 className="text-lg font-medium">Cross-Contamination Risks:</h3>
        {crossContamination.length > 0 ? (
          <ul className="list-disc list-inside text-red-600">
            {crossContamination.map((risk, index) => (
              <li key={index}>{risk}</li>
            ))}
          </ul>
        ) : (
          <p className="text-green-600">
            No cross-contamination risks detected.
          </p>
        )}
      </div>
    </div>
  );
};

export default AllergenAlerts;
