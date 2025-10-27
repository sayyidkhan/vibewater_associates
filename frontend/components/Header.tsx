"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Waves } from "lucide-react";
import { cn } from "@/lib/utils";

export default function Header() {
  const pathname = usePathname();

  const handleDashboardClick = () => {
    // Clear session storage when clicking dashboard from menu
    sessionStorage.removeItem('dashboardState');
    sessionStorage.removeItem('builderState');
  };

  return (
    <aside className="fixed left-0 top-0 z-50 h-screen w-20 border-r border-gray-800 bg-background flex flex-col items-center py-6 gap-8">
      {/* Logo */}
      <Link 
        href="/" 
        className="flex flex-col items-center gap-2" 
        title="Vibe Water Associates"
        onClick={handleDashboardClick}
      >
        <Waves className="w-8 h-8 text-primary" />
        <span className="text-[10px] font-semibold text-center leading-tight">Vibe<br/>Water</span>
      </Link>
      
      {/* Navigation */}
      <nav className="flex flex-col items-center gap-6 flex-1 mt-4">
        <Link
          href="/"
          title="Dashboard"
          onClick={handleDashboardClick}
          className={cn(
            "flex flex-col items-center gap-1 text-xs font-medium transition-colors hover:text-primary px-3 py-2 rounded-lg",
            pathname === "/" ? "text-primary bg-primary/10" : "text-gray-400"
          )}
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
          </svg>
          <span className="text-[10px]">Dashboard</span>
        </Link>
        <Link
          href="/strategies"
          title="My Strategies"
          className={cn(
            "flex flex-col items-center gap-1 text-xs font-medium transition-colors hover:text-primary px-3 py-2 rounded-lg",
            pathname === "/strategies" ? "text-primary bg-primary/10" : "text-gray-400"
          )}
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <span className="text-[10px]">Strategies</span>
        </Link>
        <Link
          href="/research"
          title="AI Research Agent"
          className={cn(
            "flex flex-col items-center gap-1 text-xs font-medium transition-colors hover:text-primary px-3 py-2 rounded-lg",
            pathname === "/research" ? "text-primary bg-primary/10" : "text-gray-400"
          )}
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <span className="text-[10px]">Research</span>
        </Link>
      </nav>
    </aside>
  );
}
