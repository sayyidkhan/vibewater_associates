"use client";

import StrategyBuilder from "@/components/StrategyBuilder";

export default function BuilderPage() {
  return (
    <div className="container mx-auto px-6 py-8">
      <div className="max-w-[1600px] mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold mb-2">Strategy Builder</h1>
          <p className="text-gray-400">
            Build your strategy visually with drag-and-drop components
          </p>
        </div>

        <StrategyBuilder />
      </div>
    </div>
  );
}
