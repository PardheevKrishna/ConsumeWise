// app/profile/components/ProfileSummary.tsx
import React from "react";

const ProfileSummary = () => {
  // Placeholder data; replace with actual data from state or backend
  const profile = {
    name: "John Doe",
    age: 30,
    dietaryPreferences: "Keto",
    allergies: "Peanuts",
    healthGoals: "Weight loss",
  };

  return (
    <div className="p-4 bg-white rounded shadow">
      <h2 className="text-xl font-semibold mb-4">Profile Summary</h2>
      <ul className="space-y-2">
        <li>
          <strong>Name:</strong> {profile.name}
        </li>
        <li>
          <strong>Age:</strong> {profile.age}
        </li>
        <li>
          <strong>Dietary Preferences:</strong> {profile.dietaryPreferences}
        </li>
        <li>
          <strong>Allergies:</strong> {profile.allergies}
        </li>
        <li>
          <strong>Health Goals:</strong> {profile.healthGoals}
        </li>
      </ul>
    </div>
  );
};

export default ProfileSummary;
