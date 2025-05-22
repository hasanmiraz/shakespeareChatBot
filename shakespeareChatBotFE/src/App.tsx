import React, { useState } from "react";
import Welcome from "./components/welcome";

export default function App() {
  const [showText, setShowText] = useState(true);
  const [input, setInput] = useState("");

  const handleInputChange = (e) => {
    setInput(e.target.value);
    if (e.target.value.trim() !== "") {
      setShowText(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col justify-between items-center bg-gray-100">
      {/* Center Text */}
      <Welcome></Welcome>

      {/* Bottom Input */}
      <div className="w-full p-4 bg-white shadow-inner">
        <input
          type="text"
          className="w-full p-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400"
          placeholder="Type something..."
          value={input}
          onChange={handleInputChange}
        />
      </div>
    </div>
  );
}
