// app/dashboard/page.tsx
"use client";

import React, { useState } from "react";
import HealthScore from "./components/HealthScore";
import NutrientAnalysis from "./components/NutrientAnalysis";
import AllergenAlerts from "./components/AllergenAlerts";
import ImpactGraphs from "./components/ImpactGraphs";
import NutrientAlerts from "./components/NutrientAlerts";
import ImageUploader from "./components/ImageUploader";
import { Analysis } from "./types/Analysis"; // Adjust the path as necessary

const DashboardPage = () => {
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [highlightedImage, setHighlightedImage] = useState<string | null>(null);

  const handleAnalysis = (data: Analysis, image: string) => {
    setAnalysis(data);
    setHighlightedImage(image);
  };

  const calculateHealthScore = (analysis: Analysis): number => {
    let health_score = 100;

    // Deduct points for bad macronutrients and micronutrients
    const bad_macronutrients = analysis.NutritionalAnalysis?.Macronutrients;
    let bad_nutrients_count = 0;
    if (bad_macronutrients) {
      ["Carbohydrates", "Proteins", "Fats", "Fiber"].forEach((nutrient) => {
        const bad =
          bad_macronutrients[nutrient as keyof typeof bad_macronutrients]?.Bad;
        if (bad && bad.length > 0) {
          bad_nutrients_count += bad.length;
        }
      });
    }
    health_score -= bad_nutrients_count * 5; // Deduct 5 points per bad nutrient

    // Deduct points for harmful ingredients
    const harmful_ingredients = analysis.HarmfulIngredients || [];
    health_score -= harmful_ingredients.length * 10; // Deduct 10 points per harmful ingredient

    // Deduct points for high processing level
    const processing_level = analysis.ProcessingLevel?.Level?.toLowerCase();
    if (processing_level === "high") {
      health_score -= 15;
    } else if (processing_level === "medium") {
      health_score -= 5;
    }

    // Deduct points for non-compliance with diets
    const non_compliant_diets =
      analysis.DietCompliance?.NonCompliantDiets || [];
    health_score -= non_compliant_diets.length * 5; // Deduct 5 points per non-compliant diet

    // Ensure the score doesn't go below 0
    health_score = Math.max(health_score, 0);

    return health_score;
  };

  return (
    <div className="space-y-8">
      <ImageUploader onAnalysis={handleAnalysis} />
      {highlightedImage && (
        <div className="mt-6">
          <h3 className="text-lg font-medium mb-2">Highlighted Image:</h3>
          <img
            src={highlightedImage}
            alt="Highlighted"
            className="w-full max-w-md"
          />
        </div>
      )}
      {analysis && (
        <>
          <HealthScore score={calculateHealthScore(analysis)} />
          <NutrientAnalysis data={analysis} />
          <AllergenAlerts data={analysis.AllergenAlerts} />
          <ImpactGraphs data={analysis.HealthImpact} />
          <NutrientAlerts data={analysis.NutrientDeficiencies} />
        </>
      )}
    </div>
  );
};

export default DashboardPage;
