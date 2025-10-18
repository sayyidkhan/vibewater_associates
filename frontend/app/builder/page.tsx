"use client";

import { useEffect, useState, useRef, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Plus, ChevronRight, Home } from "lucide-react";
import StrategyBuilder from "@/components/StrategyBuilder";
import Button from "@/components/ui/Button";

export default function BuilderPage() {
  const router = useRouter();
  const [initialData, setInitialData] = useState<any>(null);
  const currentStateRef = useRef<any>(null);
  
  useEffect(() => {
    // Load data from sessionStorage
    const savedState = sessionStorage.getItem('builderState');
    if (savedState) {
      try {
        const state = JSON.parse(savedState);
        setInitialData(state);
        currentStateRef.current = state;
        // Don't clear - keep for navigation back
      } catch (error) {
        console.error('Failed to parse builder state:', error);
      }
    }
  }, []);
  
  const handleStateChange = useCallback((state: any) => {
    currentStateRef.current = state;
  }, []);
  
  const handleDashboardClick = () => {
    // Preserve current state when navigating to dashboard
    // Save whatever state we have (could be initialData or currentState)
    const stateToSave = currentStateRef.current || initialData;
    if (stateToSave) {
      sessionStorage.setItem('dashboardState', JSON.stringify(stateToSave));
    }
    
    // Set flag to indicate we're coming from breadcrumb (to preserve state)
    sessionStorage.setItem('fromBreadcrumb', 'true');
    
    router.push('/');
  };
  
  const handleAddStrategy = () => {
    // Clear session when creating a new strategy
    sessionStorage.removeItem('dashboardState');
    sessionStorage.removeItem('builderState');
    sessionStorage.removeItem('fromBreadcrumb');
    router.push('/builder');
  };
  
  return (
    <div className="container mx-auto px-6 py-2">
      <div className="max-w-[1600px] mx-auto">
        <div className="mb-3">
          <div className="flex items-center justify-between gap-4">
            {/* Breadcrumb with title */}
            <nav className="flex items-center gap-1.5 text-sm">
              <button
                onClick={handleDashboardClick}
                className="flex items-center gap-1 text-gray-500 hover:text-primary transition-colors"
              >
                <Home className="w-3.5 h-3.5" />
                <span>Dashboard</span>
              </button>
              <ChevronRight className="w-4 h-4 text-gray-600" />
              <h1 className="text-lg font-bold text-gray-100">Strategy Builder</h1>
            </nav>
            
            <Button
              onClick={handleAddStrategy}
              className="flex items-center gap-2 flex-shrink-0"
            >
              <Plus className="w-4 h-4" />
              Add Strategy
            </Button>
          </div>
          
          {/* Subtitle */}
          <p className="text-sm text-gray-400 mt-0.5">
            Build and customize your trading strategies with AI assistance and visual flowchart editor
          </p>
        </div>

        <StrategyBuilder 
          initialData={initialData} 
          onStateChange={handleStateChange}
        />
      </div>
    </div>
  );
}
