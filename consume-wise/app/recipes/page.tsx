// app/recipes/page.tsx
import React from "react";
import RecipeList from "./components/RecipeList";

const RecipesPage = () => {
  return (
    <div className="space-y-8">
      <RecipeList />
    </div>
  );
};

export default RecipesPage;
