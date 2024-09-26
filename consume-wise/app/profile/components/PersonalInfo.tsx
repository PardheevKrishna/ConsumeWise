// app/profile/components/PersonalInfo.tsx
"use client";

import React, { useState } from "react";

const PersonalInfo = () => {
  const [formData, setFormData] = useState({
    name: "",
    age: "",
    dietaryPreferences: "",
    allergies: "",
    healthGoals: "",
  });

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Handle form submission, e.g., save to backend or state management
    console.log(formData);
  };

  return (
    <div className="p-4 bg-white rounded shadow">
      <h2 className="text-xl font-semibold mb-4">Personal Health Profile</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Name */}
        <div>
          <label htmlFor="name" className="block font-medium">
            Name
          </label>
          <input
            type="text"
            id="name"
            name="name"
            className="mt-1 block w-full border border-gray-300 rounded p-2"
            value={formData.name}
            onChange={handleChange}
            required
          />
        </div>

        {/* Age */}
        <div>
          <label htmlFor="age" className="block font-medium">
            Age
          </label>
          <input
            type="number"
            id="age"
            name="age"
            className="mt-1 block w-full border border-gray-300 rounded p-2"
            value={formData.age}
            onChange={handleChange}
            required
          />
        </div>

        {/* Dietary Preferences */}
        <div>
          <label htmlFor="dietaryPreferences" className="block font-medium">
            Dietary Preferences
          </label>
          <input
            type="text"
            id="dietaryPreferences"
            name="dietaryPreferences"
            className="mt-1 block w-full border border-gray-300 rounded p-2"
            value={formData.dietaryPreferences}
            onChange={handleChange}
            placeholder="e.g., Vegan, Keto, Paleo"
          />
        </div>

        {/* Allergies */}
        <div>
          <label htmlFor="allergies" className="block font-medium">
            Allergies
          </label>
          <input
            type="text"
            id="allergies"
            name="allergies"
            className="mt-1 block w-full border border-gray-300 rounded p-2"
            value={formData.allergies}
            onChange={handleChange}
            placeholder="e.g., Peanuts, Gluten"
          />
        </div>

        {/* Health Goals */}
        <div>
          <label htmlFor="healthGoals" className="block font-medium">
            Health Goals
          </label>
          <textarea
            id="healthGoals"
            name="healthGoals"
            className="mt-1 block w-full border border-gray-300 rounded p-2"
            value={formData.healthGoals}
            onChange={handleChange}
            placeholder="e.g., Weight loss, Muscle gain"
          ></textarea>
        </div>

        {/* Submit Button */}
        <div>
          <button
            type="submit"
            className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
          >
            Save Profile
          </button>
        </div>
      </form>
    </div>
  );
};

export default PersonalInfo;
