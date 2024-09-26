// app/planner/components/ShoppingList.tsx
import React from "react";

interface ShoppingItem {
  id: number;
  name: string;
  quantity: string;
}

const items: ShoppingItem[] = [
  { id: 1, name: "Avocados", quantity: "2" },
  { id: 2, name: "Chicken Breasts", quantity: "500g" },
  { id: 3, name: "Broccoli", quantity: "1 head" },
  // Add more items as needed
];

const ShoppingList = () => {
  return (
    <div className="p-4 bg-white rounded shadow">
      <h2 className="text-xl font-semibold mb-4">Shopping List</h2>
      <ul className="list-disc list-inside">
        {items.map((item) => (
          <li key={item.id}>
            {item.name} - {item.quantity}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default ShoppingList;
