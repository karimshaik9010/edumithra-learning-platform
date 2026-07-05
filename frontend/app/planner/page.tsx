"use client";

import React, { useState, useEffect } from "react";
import { useAuth } from "../../lib/auth";
import { apiFetch } from "../../lib/api";
import { 
  Calendar, 
  Clock, 
  CheckCircle2, 
  AlertCircle, 
  RefreshCw,
  PlayCircle,
  HelpCircle,
  TrendingUp,
  Map
} from "lucide-react";
import Link from "next/link";

interface StudySession {
  id: number;
  session_date: string;
  topic_id: number;
  topic_title: string;
  hours_scheduled: number;
  hours_completed: number;
  status: string; // Pending, Completed, Missed
}

export default function StudyPlanner() {
  const { user } = useAuth();
  const [sessions, setSessions] = useState<StudySession[]>([]);
  const [loading, setLoading] = useState(true);
  const [updatingSessionId, setUpdatingSessionId] = useState<number | null>(null);
  const [rescheduling, setRescheduling] = useState(false);

  const fetchPlannerSessions = async () => {
    try {
      const data = await apiFetch("/planner/sessions");
      setSessions(data);
    } catch (e) {
      console.error("Failed to load study sessions", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPlannerSessions();
  }, []);

  const handleUpdateStatus = async (sessionId: number, currentStatus: string, hoursSch: number) => {
    setUpdatingSessionId(sessionId);
    // Cycle status: Pending -> Completed
    const nextStatus = currentStatus === "Completed" ? "Pending" : "Completed";
    const nextHours = nextStatus === "Completed" ? hoursSch : 0.0;

    try {
      const updated = await apiFetch(`/planner/sessions/${sessionId}`, {
        method: "PUT",
        body: JSON.stringify({
          hours_completed: nextHours,
          status: nextStatus
        })
      });
      
      setSessions((prev) => 
        prev.map((s) => s.id === sessionId ? { ...s, status: updated.status, hours_completed: updated.hours_completed } : s)
      );
    } catch (e) {
      console.error("Failed to update session status", e);
    } finally {
      setUpdatingSessionId(null);
    }
  };

  const handleReschedule = async () => {
    setRescheduling(true);
    try {
      await apiFetch("/planner/regenerate", { method: "POST" });
      await fetchPlannerSessions();
    } catch (e) {
      console.error("Failed to reschedule", e);
    } finally {
      setRescheduling(false);
    }
  };

  const getDayOfWeekName = (dateStr: string) => {
    const d = new Date(dateStr);
    return d.toLocaleDateString("en-US", { weekday: 'long', month: 'short', day: 'numeric' });
  };

  if (loading) {
    return (
      <div className="flex-1 p-8 flex flex-col justify-center items-center">
        <span className="w-8 h-8 rounded-full border-2 border-indigo-500/30 border-t-indigo-500 animate-spin mb-2" />
        <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold">Aligning Calendar Schedules...</p>
      </div>
    );
  }

  return (
    <div className="flex-1 p-6 md:p-10 max-w-5xl mx-auto w-full space-y-8 relative">
      {/* Glow ambient background spot */}
      <div className="absolute top-10 right-20 w-80 h-80 bg-indigo-500/5 rounded-full blur-3xl pointer-events-none" />

      {/* Header Info */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <h1 className="text-3xl font-extrabold text-white font-outfit">
            Weekly Study Planner
          </h1>
          <p className="text-gray-400 text-sm">
            Check off topics as you learn them. Your learning analytics and Job Readiness update automatically.
          </p>
        </div>
        
        {sessions.length > 0 && (
          <button
            onClick={handleReschedule}
            disabled={rescheduling}
            className="btn-secondary px-4 py-2.5 rounded-xl text-xs font-semibold flex items-center gap-2 hover:text-indigo-300 disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${rescheduling ? "animate-spin" : ""}`} />
            Reschedule Uncompleted
          </button>
        )}
      </div>

      {sessions.length === 0 ? (
        <div className="glass-card p-12 rounded-3xl border border-dashed border-white/5 text-center flex flex-col items-center max-w-md mx-auto space-y-4">
          <Calendar className="w-10 h-10 text-gray-700" />
          <h3 className="font-bold text-lg text-white font-outfit">No sessions scheduled</h3>
          <p className="text-xs text-gray-500 leading-relaxed">
            Generate your personalized learning roadmap first to initialize your study planner calendar.
          </p>
          <Link href="/roadmap" className="glow-button px-5 py-2.5 text-xs font-semibold flex items-center gap-1.5 mt-2">
            Configure Roadmap <Map className="w-3.5 h-3.5" />
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          {sessions.map((sess) => {
            const isCompleted = sess.status === "Completed";
            
            return (
              <div 
                key={sess.id}
                className={`p-5 rounded-2xl border transition-all duration-300 flex flex-col sm:flex-row sm:items-center justify-between gap-4 ${
                  isCompleted 
                    ? "bg-teal-500/[0.01] border-teal-500/10 hover:border-teal-500/20"
                    : "bg-white/[0.01] border-white/5 hover:border-white/10"
                }`}
              >
                {/* Left: Session details */}
                <div className="space-y-2">
                  <span className="text-[10px] font-bold text-gray-500 uppercase tracking-wider flex items-center gap-1">
                    <Calendar className="w-3.5 h-3.5 text-gray-600" /> {getDayOfWeekName(sess.session_date)}
                  </span>
                  <div>
                    <h4 className={`text-base font-bold ${
                      isCompleted ? "text-gray-400 line-through" : "text-white"
                    }`}>
                      {sess.topic_title}
                    </h4>
                    <span className="text-xs text-gray-500 flex items-center gap-1 mt-1">
                      <Clock className="w-3.5 h-3.5 text-indigo-400" /> Scheduled: {sess.hours_scheduled} hours
                    </span>
                  </div>
                </div>

                {/* Right: Actions and Status */}
                <div className="flex items-center gap-3">
                  <span className={`px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                    isCompleted 
                      ? "bg-teal-500/10 border border-teal-500/20 text-teal-400" 
                      : "bg-amber-500/10 border border-amber-500/20 text-amber-400"
                  }`}>
                    {sess.status}
                  </span>

                  <button
                    onClick={() => handleUpdateStatus(sess.id, sess.status, sess.hours_scheduled)}
                    disabled={updatingSessionId !== null}
                    className={`px-4 py-2.5 rounded-xl text-xs font-semibold transition-all duration-300 flex items-center justify-center gap-1.5 border ${
                      isCompleted
                        ? "bg-white/5 border-white/5 hover:bg-white/10 text-gray-300"
                        : "bg-indigo-600/15 border-indigo-500/20 text-indigo-300 hover:bg-indigo-600/20"
                    }`}
                  >
                    {updatingSessionId === sess.id ? (
                      <span className="w-4 h-4 rounded-full border-2 border-indigo-500/30 border-t-indigo-500 animate-spin" />
                    ) : isCompleted ? (
                      <>Undo Completion</>
                    ) : (
                      <>
                        <CheckCircle2 className="w-4 h-4" />
                        Check Off
                      </>
                    )}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
