"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Waves, Plus } from "lucide-react";
import { cn } from "@/lib/utils";

export default function Header() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-50 border-b border-gray-800 bg-background">
      <div className="container mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-8">
            <Link href="/" className="flex items-center gap-2">
              <Waves className="w-6 h-6 text-primary" />
              <span className="text-xl font-semibold">Vibe Water Associates</span>
            </Link>
            
            <nav className="flex items-center gap-6">
              <Link
                href="/"
                className={cn(
                  "text-sm font-medium transition-colors hover:text-primary",
                  pathname === "/" ? "text-foreground" : "text-gray-400"
                )}
              >
                Dashboard
              </Link>
              <Link
                href="/strategies"
                className={cn(
                  "text-sm font-medium transition-colors hover:text-primary",
                  pathname === "/strategies" ? "text-primary" : "text-gray-400"
                )}
              >
                My Strategies
              </Link>
            </nav>
          </div>

          <Link
            href="/?new=true"
            className="flex items-center gap-2 px-4 py-2 bg-primary hover:bg-primary-dark text-white rounded-lg transition-colors"
          >
            <Plus className="w-4 h-4" />
            <span className="text-sm font-medium">New Strategy</span>
          </Link>
        </div>
      </div>
    </header>
  );
}
