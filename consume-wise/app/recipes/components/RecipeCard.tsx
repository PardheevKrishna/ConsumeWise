// app/recipes/components/RecipeCard.tsx
import React from "react";
import Image from "next/image";

interface Recipe {
  id: number;
  title: string;
  description: string;
  image: string;
}

interface RecipeCardProps {
  recipe: Recipe;
}

const RecipeCard: React.FC<RecipeCardProps> = ({ recipe }) => {
  return (
    <div className="border rounded-lg overflow-hidden shadow hover:shadow-lg transition-shadow duration-300">
      <Image
        src={recipe.image}
        alt={recipe.title}
        width={400}
        height={300}
        objectFit="cover"
      />
      <div className="p-4">
        <h3 className="text-lg font-semibold">{recipe.title}</h3>
        <p className="text-gray-600">{recipe.description}</p>
      </div>
    </div>
  );
};

export default RecipeCard;
