// app/profile/page.tsx
import React from "react";
import PersonalInfo from "./components/PersonalInfo";
import ProfileSummary from "./components/ProfileSummary";

const ProfilePage = () => {
  return (
    <div className="space-y-8">
      <PersonalInfo />
      <ProfileSummary />
    </div>
  );
};

export default ProfilePage;
