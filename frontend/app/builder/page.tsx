"use client";

import { useEffect, useState } from "react";
import StrategyBuilder from "@/components/StrategyBuilder";

export default function BuilderPage() {
  const [initialData, setInitialData] = useState<any>(null);
  
  useEffect(() => {
    // Load data from sessionStorage
    const savedState = sessionStorage.getItem('builderState');
    if (savedState) {
      try {
        const state = JSON.parse(savedState);
        setInitialData(state);
        // Clear after loading to avoid stale data
        sessionStorage.removeItem('builderState');
      } catch (error) {
        console.error('Failed to parse builder state:', error);
      }
    }
  }, []);
  
  return (
    <div className="container mx-auto px-6 py-8">
      <div className="max-w-[1600px] mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold mb-2">Strategy Builder</h1>
          <p className="text-gray-400">
            Build your strategy visually with drag-and-drop components
          </p>
        </div>

        <StrategyBuilder initialData={initialData} />
      </div>
    </div>
  );
}
