// components/Header.tsx
import Link from "next/link";
import React from "react";

const Header = () => {
  return (
    <header className="bg-white shadow">
      <div className="container mx-auto p-4 flex justify-between items-center">
        {/* Logo Link */}
        <Link
          href="/"
          className="text-2xl font-bold text-green-600 hover:text-green-700 transition-colors duration-300"
        >
          ConsumeWise
        </Link>

        {/* Navigation Links */}
        <nav className="space-x-4">
          <Link
            href="/dashboard"
            className="text-gray-700 hover:text-green-600 transition-colors duration-300"
          >
            Dashboard
          </Link>
          <Link
            href="/profile"
            className="text-gray-700 hover:text-green-600 transition-colors duration-300"
          >
            Profile
          </Link>
          <Link
            href="/recipes"
            className="text-gray-700 hover:text-green-600 transition-colors duration-300"
          >
            Recipes
          </Link>
          <Link
            href="/planner"
            className="text-gray-700 hover:text-green-600 transition-colors duration-300"
          >
            Planner
          </Link>
        </nav>
      </div>
    </header>
  );
};

export default Header;
