"use client";

import React from "react";
import { useAuth } from "../lib/auth";
import Sidebar from "../components/Sidebar";

export default function MainLayoutContent({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0a0a0c] flex flex-col items-center justify-center relative overflow-hidden">
        {/* Glow ambient spots */}
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse" />
        
        <div className="z-10 flex flex-col items-center gap-4">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/20 animate-bounce">
            <span className="text-xl font-bold text-white tracking-wider">E</span>
          </div>
          <div className="flex items-center gap-1.5 mt-2">
            <div className="w-2.5 h-2.5 rounded-full bg-indigo-500 animate-bounce [animation-delay:-0.3s]"></div>
            <div className="w-2.5 h-2.5 rounded-full bg-indigo-500 animate-bounce [animation-delay:-0.15s]"></div>
            <div className="w-2.5 h-2.5 rounded-full bg-indigo-500 animate-bounce"></div>
          </div>
          <p className="text-sm font-semibold tracking-wider uppercase text-gray-500 mt-2">
            Loading Copilot Experience
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0a0a0c] flex">
      {user && <Sidebar />}
      <main className={`flex-1 min-h-screen flex flex-col transition-all duration-300 ${user ? "pl-64" : ""}`}>
        {children}
      </main>
    </div>
  );
}
