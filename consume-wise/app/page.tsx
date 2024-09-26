// app/page.tsx
import React from "react";
import Image from "next/image";
import Link from "next/link";

const HomePage = () => {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen py-2">
      <Image
        src="/images/logo.png"
        alt="ConsumeWise Logo"
        width={200}
        height={200}
      />
      <h1 className="text-4xl font-bold mt-4">Welcome to ConsumeWise</h1>
      <p className="mt-2 text-lg text-center">
        Your AI-enabled smart label reader for healthier food choices.
      </p>
      <div className="mt-6">
        <Link
          href="/dashboard"
          className="px-6 py-3 bg-green-600 text-white rounded-md hover:bg-green-700"
        >
          Get Started
        </Link>
      </div>
    </div>
  );
};

export default HomePage;
