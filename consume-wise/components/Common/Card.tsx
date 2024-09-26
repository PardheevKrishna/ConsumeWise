// components/Common/Card.tsx
import React from "react";

interface CardProps {
  children: React.ReactNode;
}

const Card: React.FC<CardProps> = ({ children }) => {
  return <div className="p-4 bg-white rounded shadow">{children}</div>;
};

export default Card;
