// components/Footer.tsx
import React from "react";

const Footer = () => {
  return (
    <footer className="bg-white shadow mt-8">
      <div className="container mx-auto p-4 text-center text-gray-500">
        &copy; {new Date().getFullYear()} ConsumeWise. All rights reserved.
      </div>
    </footer>
  );
};

export default Footer;
