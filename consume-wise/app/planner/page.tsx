// app/planner/page.tsx

'use client'

import React from "react";
import MealPlanner from "./components/MealPlanner";
import ShoppingList from "./components/ShoppingList";

const PlannerPage = () => {
  return (
    <div className="space-y-8">
      <MealPlanner />
      <ShoppingList />
    </div>
  );
};

export default PlannerPage;
