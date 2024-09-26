// app/planner/components/MealPlanner.tsx
import React, { useState } from "react";

const MealPlanner = () => {
  const [meals, setMeals] = useState({
    Monday: "",
    Tuesday: "",
    Wednesday: "",
    Thursday: "",
    Friday: "",
    Saturday: "",
    Sunday: "",
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setMeals({
      ...meals,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Handle meal planning logic, e.g., save to backend or state management
    console.log(meals);
  };

  return (
    <div className="p-4 bg-white rounded shadow">
      <h2 className="text-xl font-semibold mb-4">Meal Planner</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        {Object.keys(meals).map((day) => (
          <div key={day}>
            <label htmlFor={day} className="block font-medium">
              {day}
            </label>
            <input
              type="text"
              id={day}
              name={day}
              className="mt-1 block w-full border border-gray-300 rounded p-2"
              value={meals[day as keyof typeof meals]}
              onChange={handleChange}
              placeholder={`Enter meal for ${day}`}
            />
          </div>
        ))}
        <button
          type="submit"
          className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
        >
          Save Meal Plan
        </button>
      </form>
    </div>
  );
};

export default MealPlanner;
