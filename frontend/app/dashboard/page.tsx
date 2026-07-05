"use client";

import React, { useState, useEffect } from "react";
import { useAuth } from "../../lib/auth";
import { apiFetch } from "../../lib/api";
import { 
  Zap, 
  Clock, 
  CheckCircle, 
  TrendingUp, 
  ChevronRight, 
  AlertCircle,
  HelpCircle,
  Lightbulb,
  Terminal,
  FileText,
  Lock
} from "lucide-react";
import Link from "next/link";

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

export default function Dashboard() {
  const { user } = useAuth();
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchAnalytics = async () => {
    try {
      const res = await apiFetch("/analytics/");
      setData(res);
    } catch (e) {
      console.error("Failed to load dashboard data", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  if (loading) {
    return (
      <div className="flex-1 p-8 flex flex-col justify-center items-center">
        <span className="w-8 h-8 rounded-full border-2 border-indigo-500/30 border-t-indigo-500 animate-spin mb-2" />
        <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold">Consolidating Analytics...</p>
      </div>
    );
  }

  const statCards = [
    {
      title: "Learning Streak",
      value: `${data?.learning_streak || 0} Days`,
      desc: "Consecutive study days",
      icon: Zap,
      color: "from-amber-500/10 to-orange-500/10 border-amber-500/20 text-amber-400"
    },
    {
      title: "Syllabus Progress",
      value: `${data?.completed_topics_count || 0}/${data?.total_topics_count || 0}`,
      desc: `${Math.round((data?.learning_progress || 0) * 100)}% topics complete`,
      icon: CheckCircle,
      color: "from-teal-500/10 to-emerald-500/10 border-teal-500/20 text-teal-400"
    },
    {
      title: "Hours Logged",
      value: `${data?.weekly_study_time || 0.0} hrs`,
      desc: "Completed study this week",
      icon: Clock,
      color: "from-indigo-500/10 to-purple-500/10 border-indigo-500/20 text-indigo-400"
    },
    {
      title: "Job Readiness Score",
      value: `${data?.job_readiness || 10}%`,
      desc: "Weighted readiness index",
      icon: TrendingUp,
      color: "from-pink-500/10 to-rose-500/10 border-pink-500/20 text-pink-400"
    }
  ];

  return (
    <div className="flex-1 p-6 md:p-10 space-y-8 max-w-7xl mx-auto w-full relative">
      {/* Background flare */}
      <div className="absolute top-0 right-10 w-96 h-96 bg-indigo-500/5 rounded-full blur-3xl pointer-events-none" />

      {/* Header Greeting */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-white font-outfit">
            Welcome back, {user?.name}!
          </h1>
          <p className="text-gray-400 text-sm mt-1">
            Track your progress, review your customized learning schedule, and check your readiness score.
          </p>
        </div>
        <Link href="/roadmap" className="glow-button px-5 py-3 text-sm font-semibold tracking-wide inline-flex items-center gap-2">
          View Roadmap
          <ChevronRight className="w-4 h-4" />
        </Link>
      </div>

      {/* Metrics Row */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((card, idx) => {
          const Icon = card.icon;
          return (
            <div key={idx} className={`glass-card p-6 rounded-2xl border bg-gradient-to-tr ${card.color} flex flex-col justify-between`}>
              <div className="flex justify-between items-start">
                <span className="text-xs font-semibold uppercase tracking-wider text-gray-400">{card.title}</span>
                <div className="p-2 rounded-xl bg-white/5 border border-white/5">
                  <Icon className="w-5 h-5" />
                </div>
              </div>
              <div className="mt-4">
                <h2 className="text-3xl font-bold tracking-tight text-white font-outfit">{card.value}</h2>
                <p className="text-xs text-gray-500 mt-1">{card.desc}</p>
              </div>
            </div>
          );
        })}
      </div>

      {/* AI Mentor Insights */}
      <div className="glass-card p-6 rounded-3xl border border-indigo-500/20 bg-gradient-to-r from-indigo-950/20 via-black/40 to-transparent flex items-start gap-4">
        <div className="p-3 rounded-2xl bg-indigo-500/15 border border-indigo-500/30 text-indigo-400 shrink-0">
          <Lightbulb className="w-6 h-6 text-indigo-400 animate-pulse" />
        </div>
        <div>
          <h3 className="font-bold text-sm tracking-wide text-indigo-300 font-outfit uppercase">
            AI Mentor Recommendation
          </h3>
          <p className="text-gray-300 text-sm leading-relaxed mt-2 font-medium">
            {data?.ai_insights}
          </p>
        </div>
      </div>

      {/* Skills Tracker */}
      <div className="space-y-6">
          <div className="glass-card p-6 rounded-3xl">
            <h3 className="font-bold text-lg text-white font-outfit mb-4">Skills Progress Map</h3>
            
            {data && Object.keys(data.skills_progress).length > 0 ? (
              <div className="space-y-4">
                {Object.entries(data.skills_progress).map(([name, progress]) => (
                  <div key={name} className="space-y-2">
                    <div className="flex justify-between text-xs font-semibold">
                      <span className="text-gray-300 truncate max-w-[80%]">{name}</span>
                      <span className="text-indigo-400">{Math.round(progress)}%</span>
                    </div>
                    <div className="h-2 w-full bg-white/5 rounded-full overflow-hidden border border-white/5">
                      <div 
                        className="h-full bg-gradient-to-r from-indigo-500 to-purple-600 rounded-full transition-all duration-500"
                        style={{ width: `${progress}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-8 text-center bg-white/[0.02] rounded-2xl border border-dashed border-white/5 text-gray-500 text-sm">
                No active skills mapped. Please generate a roadmap to see breakdown.
              </div>
            )}
          </div>
        </div>

    </div>
  );
}
