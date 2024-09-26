// app/dashboard/page.tsx
import React from "react";
import HealthScore from "./components/HealthScore";
import NutrientAnalysis from "./components/NutrientAnalysis";
import AllergenAlerts from "./components/AllergenAlerts";
import ImpactGraphs from "./components/ImpactGraphs";
import NutrientAlerts from "./components/NutrientAlerts";
import ImageUploader from "./components/ImageUploader";

const DashboardPage = () => {
  return (
    <div className="space-y-8">
      <ImageUploader />
      <HealthScore score={85} />
      <NutrientAnalysis />
      <AllergenAlerts />
      <ImpactGraphs />
      <NutrientAlerts />
    </div>
  );
};

export default DashboardPage;
