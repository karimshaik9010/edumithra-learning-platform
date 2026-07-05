"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "../lib/auth";
import { 
  LayoutDashboard, 
  Map, 
  MessageSquare, 
  Calendar, 
  TrendingUp, 
  Video, 
  Award, 
  Zap, 
  LogOut,
  Sparkles,
  BookOpen
} from "lucide-react";

export default function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  const navItems: { name: string; href: string; icon: React.ComponentType<React.SVGProps<SVGSVGElement>>; highlight?: boolean }[] = [
    { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
    { name: "Personalized Roadmap", href: "/roadmap", icon: Map },
    { name: "Weekly Planner", href: "/planner", icon: Calendar },
    { name: "Progress Analytics", href: "/analytics", icon: TrendingUp },
    { name: "Job Readiness Score", href: "/readiness", icon: Award },
  ];

  if (!user) return null;

  return (
    <aside className="w-64 border-r border-white/5 bg-black/40 backdrop-blur-xl flex flex-col h-screen fixed left-0 top-0 text-white z-40">
      {/* Brand Header */}
      <div className="p-6 flex items-center gap-3 border-b border-white/5">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
          <BookOpen className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="font-extrabold text-lg tracking-tight bg-gradient-to-r from-indigo-300 to-purple-400 bg-clip-text text-transparent">
            EDUMITHRA
          </h1>
          <span className="text-[10px] text-gray-500 font-medium tracking-wider uppercase">
            AI Learning Copilot
          </span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-6 space-y-1.5 overflow-y-auto">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 group ${
                isActive 
                  ? item.highlight 
                    ? "bg-gradient-to-r from-amber-500/20 to-orange-500/20 border border-amber-500/30 text-amber-300"
                    : "bg-indigo-600/15 border border-indigo-500/30 text-indigo-300"
                  : item.highlight
                    ? "hover:bg-amber-500/5 text-amber-400/80 hover:text-amber-300 border border-transparent"
                    : "hover:bg-white/5 text-gray-400 hover:text-white border border-transparent"
              }`}
            >
              <Icon className={`w-5 h-5 transition-transform duration-300 group-hover:scale-110 ${
                isActive 
                  ? item.highlight ? "text-amber-400" : "text-indigo-400"
                  : "text-gray-500 group-hover:text-gray-300"
              }`} />
              <span className="text-sm font-medium tracking-wide">{item.name}</span>
              {item.highlight && (
                <Sparkles className="w-3.5 h-3.5 ml-auto text-amber-400 animate-pulse" />
              )}
            </Link>
          );
        })}
      </nav>

      {/* User Footer Profile */}
      <div className="p-4 border-t border-white/5 bg-white/[0.02]">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center font-bold text-indigo-400 shadow-inner">
            {user.name.charAt(0).toUpperCase()}
          </div>
          <div className="flex-1 overflow-hidden">
            <h4 className="text-sm font-semibold truncate text-gray-200">{user.name}</h4>
            <span className="text-xs text-indigo-400 flex items-center gap-1 font-medium">
              <Zap className="w-3 h-3 text-amber-500 fill-amber-500" /> {user.streak} Day Streak
            </span>
          </div>
        </div>
        <button
          onClick={logout}
          className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl text-xs font-semibold tracking-wide border border-white/5 hover:border-red-500/20 text-gray-400 hover:text-red-400 hover:bg-red-500/5 transition-all duration-300"
        >
          <LogOut className="w-4 h-4" />
          Sign Out
        </button>
      </div>
    </aside>
  );
}
