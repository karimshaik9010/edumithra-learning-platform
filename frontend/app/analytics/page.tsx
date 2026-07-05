"use client";

import React, { useState, useEffect } from "react";
import { useAuth } from "../../lib/auth";
import { apiFetch } from "../../lib/api";
import { 
  TrendingUp, 
  Map, 
  HelpCircle, 
  Award, 
  Activity,
  CheckCircle,
  FileCheck
} from "lucide-react";
import Link from "next/link";
import { 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer,
  BarChart,
  Bar,
  Cell
} from "recharts";

interface DecisionLog {
  id: number;
  event_name: string;
  timestamp: string;
  description: string;
}

interface AnalyticsData {
  learning_progress: number;
  weekly_study_time: number;
  learning_streak: number;
  completed_topics_count: number;
  total_topics_count: number;
  job_readiness: number;
  recent_quiz_score: number;
  skills_progress: Record<string, number>;
  ai_insights: string;
  recent_logs: DecisionLog[];
}

export default function Analytics() {
  const { user } = useAuth();
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    const fetchAnalyticsData = async () => {
      try {
        const res = await apiFetch("/analytics/");
        setData(res);
      } catch (e) {
        console.error("Failed to load analytics data", e);
      } finally {
        setLoading(false);
      }
    };
    fetchAnalyticsData();
  }, []);

  if (loading || !mounted) {
    return (
      <div className="flex-1 p-8 flex flex-col justify-center items-center">
        <span className="w-8 h-8 rounded-full border-2 border-indigo-500/30 border-t-indigo-500 animate-spin mb-2" />
        <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold">Generating Statistical Charts...</p>
      </div>
    );
  }

  // Fallback / standard charts data
  const weeklyTrendData = [
    { name: "Mon", hours: 1.5 },
    { name: "Tue", hours: 2.0 },
    { name: "Wed", hours: data?.weekly_study_time ? Math.min(data.weekly_study_time / 3, 2.5) : 1.0 },
    { name: "Thu", hours: 0.5 },
    { name: "Fri", hours: data?.weekly_study_time ? Math.min(data.weekly_study_time / 2, 3.0) : 2.0 },
    { name: "Sat", hours: 0.0 },
    { name: "Sun", hours: 1.0 }
  ];

  // Map skills progress record to array format for Recharts Bar chart
  const skillsData = data && Object.keys(data.skills_progress).length > 0
    ? Object.entries(data.skills_progress).map(([name, val]) => ({
        name: name.substring(0, 18) + (name.length > 18 ? "..." : ""),
        progress: Math.round(val)
      }))
    : [
        { name: "Phases 1 Foundations", progress: 0 },
        { name: "Phases 2 Core Systems", progress: 0 },
        { name: "Phases 3 Advanced API", progress: 0 }
      ];

  const BAR_COLORS = ["#6366f1", "#14b8a6", "#ec4899", "#f59e0b"];

  return (
    <div className="flex-1 p-6 md:p-10 max-w-7xl mx-auto w-full space-y-8 relative">
      {/* Ambient backgrounds */}
      <div className="absolute top-10 right-10 w-96 h-96 bg-indigo-500/5 rounded-full blur-3xl pointer-events-none" />

      {/* Header Info */}
      <div className="space-y-1">
        <h1 className="text-3xl font-extrabold text-white font-outfit">
          Progress Analytics
        </h1>
        <p className="text-gray-400 text-sm">
          Detailed metrics charting course milestone completion, study effort allocation, and mock exam trends.
        </p>
      </div>

      {!data || data.total_topics_count === 0 ? (
        <div className="glass-card p-12 rounded-3xl border border-dashed border-white/5 text-center flex flex-col items-center max-w-md mx-auto space-y-4">
          <Activity className="w-10 h-10 text-gray-700 animate-pulse" />
          <h3 className="font-bold text-lg text-white font-outfit">No analytics computed</h3>
          <p className="text-xs text-gray-500 leading-relaxed">
            Please configure and initiate your active learning roadmap first to populate dashboard analytics.
          </p>
          <Link href="/roadmap" className="glow-button px-5 py-2.5 text-xs font-semibold flex items-center gap-1.5 mt-2">
            Configure Roadmap <Map className="w-3.5 h-3.5" />
          </Link>
        </div>
      ) : (
        <div className="space-y-8">
          
          {/* Summary Metric Rings/Cards */}
          <div className="grid sm:grid-cols-3 gap-6">
            <div className="glass-card p-6 rounded-2xl border border-white/5 flex items-center gap-4">
              <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
                <CheckCircle className="w-6 h-6" />
              </div>
              <div>
                <h4 className="text-2xl font-bold text-white font-outfit">
                  {Math.round(data.learning_progress * 100)}%
                </h4>
                <p className="text-xs text-gray-500 font-semibold uppercase tracking-wider">Roadmap Complete</p>
              </div>
            </div>

            <div className="glass-card p-6 rounded-2xl border border-white/5 flex items-center gap-4">
              <div className="w-12 h-12 rounded-2xl bg-teal-500/10 border border-teal-500/20 flex items-center justify-center text-teal-400">
                <FileCheck className="w-6 h-6" />
              </div>
              <div>
                <h4 className="text-2xl font-bold text-white font-outfit">
                  {data.recent_quiz_score ? `${Math.round(data.recent_quiz_score)}%` : "N/A"}
                </h4>
                <p className="text-xs text-gray-500 font-semibold uppercase tracking-wider">Avg Assessment Score</p>
              </div>
            </div>

            <div className="glass-card p-6 rounded-2xl border border-white/5 flex items-center gap-4">
              <div className="w-12 h-12 rounded-2xl bg-pink-500/10 border border-pink-500/20 flex items-center justify-center text-pink-400">
                <Award className="w-6 h-6" />
              </div>
              <div>
                <h4 className="text-2xl font-bold text-white font-outfit">{data.job_readiness}%</h4>
                <p className="text-xs text-gray-500 font-semibold uppercase tracking-wider">Job Readiness index</p>
              </div>
            </div>
          </div>

          {/* Charts Row */}
          <div className="grid lg:grid-cols-2 gap-8">
            
            {/* Area Chart: Study Hours */}
            <div className="glass-card p-6 rounded-3xl border border-white/5">
              <h3 className="font-bold text-base text-white font-outfit mb-6">Weekly Study Hours Trend</h3>
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={weeklyTrendData} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
                    <defs>
                      <linearGradient id="colorHours" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#6366f1" stopOpacity={0.25}/>
                        <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <XAxis dataKey="name" stroke="#52525b" fontSize={11} tickLine={false} />
                    <YAxis stroke="#52525b" fontSize={11} tickLine={false} />
                    <Tooltip 
                      contentStyle={{ backgroundColor: "rgba(20, 20, 25, 0.9)", border: "1px solid rgba(255,255,255,0.08)", borderRadius: "12px" }}
                      labelStyle={{ color: "#fff", fontWeight: "bold", fontSize: 12 }}
                      itemStyle={{ color: "#818cf8" }}
                    />
                    <Area type="monotone" dataKey="hours" stroke="#6366f1" strokeWidth={2.5} fillOpacity={1} fill="url(#colorHours)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Bar Chart: Skill Domains */}
            <div className="glass-card p-6 rounded-3xl border border-white/5">
              <h3 className="font-bold text-base text-white font-outfit mb-6">Milestone Sub-Domain Mastery</h3>
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={skillsData} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
                    <XAxis dataKey="name" stroke="#52525b" fontSize={10} tickLine={false} />
                    <YAxis stroke="#52525b" fontSize={11} tickLine={false} domain={[0, 100]} />
                    <Tooltip 
                      contentStyle={{ backgroundColor: "rgba(20, 20, 25, 0.9)", border: "1px solid rgba(255,255,255,0.08)", borderRadius: "12px" }}
                      itemStyle={{ color: "#2dd4bf" }}
                    />
                    <Bar dataKey="progress" radius={[8, 8, 0, 0]}>
                      {skillsData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={BAR_COLORS[index % BAR_COLORS.length]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

          </div>

        </div>
      )}
    </div>
  );
}
