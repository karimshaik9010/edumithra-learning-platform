"use client";

import React, { useState, useEffect } from "react";
import { useAuth } from "../../lib/auth";
import { apiFetch } from "../../lib/api";
import { Award, Map } from "lucide-react";
import Link from "next/link";

interface ReadinessReport {
  score: number;
}

export default function JobReadiness() {
  const { user } = useAuth();
  const [report, setReport] = useState<ReadinessReport | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchReadinessReport = async () => {
    try {
      const data = await apiFetch("/readiness/");
      setReport(data);
    } catch (e) {
      console.error("Failed to load readiness report", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReadinessReport();
  }, []);

  if (loading) {
    return (
      <div className="flex-1 p-8 flex flex-col justify-center items-center">
        <span className="w-8 h-8 rounded-full border-2 border-indigo-500/30 border-t-indigo-500 animate-spin mb-2" />
        <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold">Calculating Job Readiness Metrics...</p>
      </div>
    );
  }

  const getStatusLabel = (score: number) => {
    if (score <= 30) return "Beginner";
    if (score <= 60) return "Developing";
    if (score <= 85) return "Job Ready";
    return "Highly Prepared";
  };

  return (
    <div className="flex-1 p-6 md:p-10 max-w-4xl mx-auto w-full space-y-8 relative flex flex-col items-center justify-center min-h-[80vh]">
      {/* Background radial flare */}
      <div className="absolute top-10 right-10 w-96 h-96 bg-indigo-500/5 rounded-full blur-3xl pointer-events-none" />

      {/* Header Info */}
      <div className="text-center space-y-2 mb-8">
        <h1 className="text-3xl font-extrabold text-white font-outfit">
          Job Readiness Tracker
        </h1>
        <p className="text-gray-400 text-sm max-w-lg mx-auto">
          A real-time evaluation of your market alignment computed based on syllabus logs, quiz scores, and roadmap completion.
        </p>
      </div>

      {!report ? (
        <div className="glass-card p-12 rounded-3xl border border-dashed border-white/5 text-center flex flex-col items-center max-w-md mx-auto space-y-4">
          <Award className="w-10 h-10 text-gray-700" />
          <h3 className="font-bold text-lg text-white font-outfit">No profile metrics found</h3>
          <p className="text-xs text-gray-500 leading-relaxed">
            Generate and progress through your learning roadmap to build your market readiness report.
          </p>
          <Link href="/roadmap" className="glow-button px-5 py-2.5 text-xs font-semibold flex items-center gap-1.5 mt-2">
            Configure Roadmap <Map className="w-3.5 h-3.5" />
          </Link>
        </div>
      ) : (
        <div className="w-full max-w-md">
          {/* Centered Minimal Card */}
          <div className="glass-card p-10 rounded-[2.5rem] border border-white/5 shadow-2xl bg-gradient-to-b from-white/[0.03] to-transparent flex flex-col items-center justify-center text-center space-y-8">
            <h3 className="font-bold text-sm text-gray-400 uppercase tracking-wider font-outfit">
              Readiness Score
            </h3>
            
            {/* Visual Circular Progress Ring */}
            <div className="relative w-48 h-48 flex items-center justify-center">
              <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                {/* Background Ring */}
                <circle 
                  cx="50" 
                  cy="50" 
                  r="42" 
                  stroke="rgba(255, 255, 255, 0.03)" 
                  strokeWidth="8" 
                  fill="transparent" 
                />
                {/* Foreground Ring */}
                <circle 
                  cx="50" 
                  cy="50" 
                  r="42" 
                  stroke="url(#grad)" 
                  strokeWidth="8" 
                  strokeDasharray="264" 
                  strokeDashoffset={264 - (264 * report.score) / 100} 
                  strokeLinecap="round" 
                  fill="transparent" 
                  className="transition-all duration-1000 ease-out"
                />
                {/* Gradient Definition */}
                <defs>
                  <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#6366f1" />
                    <stop offset="100%" stopColor="#ec4899" />
                  </linearGradient>
                </defs>
              </svg>
              <div className="absolute flex flex-col items-center">
                <span className="text-5xl font-extrabold text-white font-outfit">{report.score}%</span>
              </div>
            </div>

            <div className="space-y-3 pt-2">
              <div className="inline-block px-4 py-1.5 rounded-full bg-white/5 border border-white/10">
                <h4 className="font-bold text-sm text-white font-outfit tracking-wide">
                  {getStatusLabel(report.score)}
                </h4>
              </div>
              <p className="text-sm text-gray-400 leading-relaxed max-w-sm">
                Continue completing your roadmap to improve your readiness.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
