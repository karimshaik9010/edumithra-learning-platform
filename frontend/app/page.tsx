"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "../lib/auth";
import { 
  Sparkles, 
  ShieldCheck, 
  Map, 
  MessageSquare, 
  Zap, 
  BookOpen, 
  Target,
  Calendar
} from "lucide-react";

export default function Home() {
  const router = useRouter();
  const { user, login, register } = useAuth();
  
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [error, setError] = useState("");
  const [formLoading, setFormLoading] = useState(false);

  // If already logged in, skip landing page
  useEffect(() => {
    if (user) {
      router.push("/dashboard");
    }
  }, [user, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setFormLoading(true);

    try {
      if (isLogin) {
        await login(email, password);
      } else {
        if (!name) {
          setError("Name is required");
          setFormLoading(false);
          return;
        }
        await register(email, password, name);
      }
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message || "Authentication failed. Please check inputs.");
    } finally {
      setFormLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a0c] flex flex-col justify-center relative overflow-hidden px-4 md:px-8 py-10">
      {/* Background gradients */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[350px] bg-indigo-500/5 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute -top-40 -left-40 w-96 h-96 bg-purple-500/5 rounded-full blur-[100px] pointer-events-none" />
      <div className="absolute bottom-10 right-10 w-[400px] h-[400px] bg-teal-500/5 rounded-full blur-[120px] pointer-events-none" />

      <div className="max-w-6xl mx-auto w-full grid md:grid-cols-12 gap-12 items-center z-10">
        
        {/* Left Side: Product Intro */}
        <div className="md:col-span-7 text-left space-y-6">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-xs font-semibold text-indigo-400">
            <Sparkles className="w-3.5 h-3.5" />
            Empowered by Groq LLM Inference
          </div>
          
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight leading-tight text-white font-outfit">
            Your Personal AI Mentor <br />
            <span className="bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-500 bg-clip-text text-transparent">
              That Learns With You.
            </span>
          </h1>
          
          <p className="text-gray-400 text-lg leading-relaxed max-w-xl">
            EDUMITHRA generates highly customized learning roadmaps, designs adaptive weekly calendars, 
            and recalculates your Job Readiness Score in real time.
          </p>

          <div className="grid sm:grid-cols-2 gap-4 pt-4">
            <div className="flex gap-3 items-start p-4 rounded-2xl bg-white/[0.02] border border-white/5">
              <div className="w-8 h-8 rounded-lg bg-indigo-500/15 flex items-center justify-center text-indigo-400 shrink-0">
                <Map className="w-4 h-4" />
              </div>
              <div>
                <h4 className="font-semibold text-sm text-gray-200">Adaptive Roadmap</h4>
                <p className="text-xs text-gray-500 mt-1">Syllabus adapts dynamically based on your test score failures.</p>
              </div>
            </div>
            
        

            <div className="flex gap-3 items-start p-4 rounded-2xl bg-white/[0.02] border border-white/5">
              <div className="w-8 h-8 rounded-lg bg-teal-500/15 flex items-center justify-center text-teal-400 shrink-0">
                <Calendar className="w-4 h-4" />
              </div>
              <div>
                <h4 className="font-semibold text-sm text-gray-200">Weekly Planner</h4>
                <p className="text-xs text-gray-500 mt-1">Generate manageable weekly study schedules aligned with your goals.</p>
              </div>
            </div>

            <div className="flex gap-3 items-start p-4 rounded-2xl bg-white/[0.02] border border-white/5">
              <div className="w-8 h-8 rounded-lg bg-amber-500/15 flex items-center justify-center text-amber-400 shrink-0">
                <Target className="w-4 h-4" />
              </div>
              <div>
                <h4 className="font-semibold text-sm text-gray-200">Readiness Score</h4>
                <p className="text-xs text-gray-500 mt-1">Quantifiable career readiness track recalculated automatically.</p>
              </div>
            </div>
          </div>
        </div>

        {/* Right Side: Auth Card Form */}
        <div className="md:col-span-5">
          <div className="glass-card p-8 rounded-3xl relative overflow-hidden">
            {/* Ambient card background */}
            <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-500/10 rounded-full blur-2xl pointer-events-none" />
            
            <div className="flex items-center gap-3 mb-6">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center">
                <BookOpen className="w-4 h-4 text-white" />
              </div>
              <h2 className="text-xl font-bold tracking-tight text-white font-outfit">
                {isLogin ? "Welcome Back" : "Start Learning"}
              </h2>
            </div>

            {error && (
              <div className="mb-4 p-3.5 rounded-xl bg-red-500/10 border border-red-500/20 text-xs font-medium text-red-400">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              {!isLogin && (
                <div>
                  <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Name</label>
                  <input
                    type="text"
                    required
                    placeholder="Enter your name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="w-full px-4 py-3 glass-input text-sm"
                  />
                </div>
              )}

              <div>
                <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Email Address</label>
                <input
                  type="email"
                  required
                  placeholder="name@domain.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-4 py-3 glass-input text-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Password</label>
                <input
                  type="password"
                  required
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-4 py-3 glass-input text-sm"
                />
              </div>

              <button
                type="submit"
                disabled={formLoading}
                className="w-full py-3.5 glow-button text-sm font-semibold tracking-wide flex items-center justify-center gap-2 mt-2 disabled:opacity-50"
              >
                {formLoading ? (
                  <span className="w-5 h-5 rounded-full border-2 border-white/30 border-t-white animate-spin" />
                ) : (
                  <>
                    <ShieldCheck className="w-4 h-4" />
                    {isLogin ? "Sign In to Copilot" : "Generate Account"}
                  </>
                )}
              </button>
            </form>

            <div className="mt-6 pt-6 border-t border-white/5 text-center">
              <button
                onClick={() => {
                  setIsLogin(!isLogin);
                  setError("");
                }}
                className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 transition-colors"
              >
                {isLogin ? "New to EDUMITHRA? Sign Up" : "Already have an account? Sign In"}
              </button>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
