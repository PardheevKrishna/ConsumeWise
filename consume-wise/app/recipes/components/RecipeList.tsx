// app/recipes/components/RecipeList.tsx
import React from "react";
import RecipeCard from "./RecipeCard";

interface Recipe {
  id: number;
  title: string;
  description: string;
  image: string;
}

const recipes: Recipe[] = [
  {
    id: 1,
    title: "Keto Avocado Salad",
    description: "A healthy and filling keto-friendly avocado salad.",
    image: "/images/recipes/avocado-salad.jpg",
  },
  {
    id: 2,
    title: "Grilled Chicken with Veggies",
    description: "Delicious grilled chicken served with steamed vegetables.",
    image: "/images/recipes/grilled-chicken.jpg",
  },
  // Add more recipes as needed
];

const RecipeList = () => {
  return (
    <div className="p-4 bg-white rounded shadow">
      <h2 className="text-xl font-semibold mb-4">Recipe Suggestions</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {recipes.map((recipe) => (
          <RecipeCard key={recipe.id} recipe={recipe} />
        ))}
      </div>
    </div>
  );
};

export default RecipeList;
