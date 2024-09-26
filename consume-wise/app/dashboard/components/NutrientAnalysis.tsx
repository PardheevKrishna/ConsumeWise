// app/dashboard/components/NutrientAnalysis.tsx
"use client";

import React from "react";
import { Analysis } from "../types/Analysis"; // Adjust the path as necessary
import classNames from "classnames";

interface NutrientAnalysisProps {
  data: Analysis;
}

const NutrientAnalysis: React.FC<NutrientAnalysisProps> = ({ data }) => {
  const { NutritionalAnalysis, ProcessingLevel, HarmfulIngredients } = data;

  const renderMacronutrients = () => {
    if (!NutritionalAnalysis?.Macronutrients) return null;

    return (
      <div className="mb-4">
        <h3 className="text-lg font-semibold">Macronutrients</h3>
        {Object.entries(NutritionalAnalysis.Macronutrients).map(
          ([key, value]) => (
            <div key={key} className="mt-2">
              <h4 className="font-medium">{key}:</h4>
              {value.Good && value.Good.length > 0 && (
                <p className="text-green-600">
                  <strong>Good:</strong> {value.Good.join(", ")}
                </p>
              )}
              {value.Bad && value.Bad.length > 0 && (
                <p className="text-red-600">
                  <strong>Bad:</strong> {value.Bad.join(", ")}
                </p>
              )}
            </div>
          )
        )}
      </div>
    );
  };

  const renderMicronutrients = () => {
    if (!NutritionalAnalysis?.Micronutrients) return null;

    return (
      <div className="mb-4">
        <h3 className="text-lg font-semibold">Micronutrients</h3>
        {Object.entries(NutritionalAnalysis.Micronutrients).map(
          ([key, value]) => (
            <div key={key} className="mt-2">
              <h4 className="font-medium">{key}:</h4>
              {value.Good && value.Good.length > 0 && (
                <p className="text-green-600">
                  <strong>Good:</strong> {value.Good.join(", ")}
                </p>
              )}
              {value.Deficient && value.Deficient.length > 0 && (
                <p className="text-red-600">
                  <strong>Deficient:</strong> {value.Deficient.join(", ")}
                </p>
              )}
            </div>
          )
        )}
      </div>
    );
  };

  const renderHealthRisks = () => {
    if (
      !NutritionalAnalysis?.HealthRisks ||
      NutritionalAnalysis.HealthRisks.length === 0
    )
      return null;

    return (
      <div className="mb-4">
        <h3 className="text-lg font-semibold">Health Risks</h3>
        <ul className="list-disc list-inside text-red-600">
          {NutritionalAnalysis.HealthRisks.map((risk, index) => (
            <li key={index}>{risk}</li>
          ))}
        </ul>
      </div>
    );
  };

  const renderHealthBenefits = () => {
    if (
      !NutritionalAnalysis?.HealthBenefits ||
      NutritionalAnalysis.HealthBenefits.length === 0
    )
      return null;

    return (
      <div className="mb-4">
        <h3 className="text-lg font-semibold">Health Benefits</h3>
        <ul className="list-disc list-inside text-green-600">
          {NutritionalAnalysis.HealthBenefits.map((benefit, index) => (
            <li key={index}>{benefit}</li>
          ))}
        </ul>
      </div>
    );
  };

  const renderProcessingLevel = () => {
    if (!ProcessingLevel) return null;

    const { Level, Description, Good, Bad } = ProcessingLevel;
    const color = classNames({
      "text-green-600": Level?.toLowerCase() === "low",
      "text-orange-600": Level?.toLowerCase() === "medium",
      "text-red-600": Level?.toLowerCase() === "high",
      "text-gray-600": true,
    });

    return (
      <div className="mb-4">
        <h3 className="text-lg font-semibold">Processing Level</h3>
        <p className={color}>
          <strong>Level:</strong> {Level}
        </p>
        <p>{Description}</p>
        {Good && Good.length > 0 && (
          <div className="mt-2">
            <p className="text-green-600">
              <strong>Good Aspects:</strong> {Good.join(", ")}
            </p>
          </div>
        )}
        {Bad && Bad.length > 0 && (
          <div className="mt-2">
            <p className="text-red-600">
              <strong>Bad Aspects:</strong> {Bad.join(", ")}
            </p>
          </div>
        )}
      </div>
    );
  };

  const renderHarmfulIngredients = () => {
    if (!HarmfulIngredients || HarmfulIngredients.length === 0) return null;

    return (
      <div className="mb-4">
        <h3 className="text-lg font-semibold">Harmful Ingredients</h3>
        <ul className="list-disc list-inside text-red-600">
          {HarmfulIngredients.map((ingredient, index) => (
            <li key={index}>
              <strong>{ingredient.Ingredient}:</strong> {ingredient.Reason}
            </li>
          ))}
        </ul>
      </div>
    );
  };

  return (
    <div className="p-4 bg-white rounded shadow">
      <h2 className="text-xl font-semibold mb-4">Nutritional Analysis</h2>
      {renderMacronutrients()}
      {renderMicronutrients()}
      {renderHealthRisks()}
      {renderHealthBenefits()}
      {renderProcessingLevel()}
      {renderHarmfulIngredients()}
      {/* Add more sections as needed */}
    </div>
  );
};

export default NutrientAnalysis;
