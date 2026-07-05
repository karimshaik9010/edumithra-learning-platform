"use client";

import React, { useState, useEffect } from "react";
import { useAuth } from "../../lib/auth";
import { apiFetch } from "../../lib/api";
import {
  Sparkles,
  CheckCircle,
  Circle,
  Calendar,
  BookOpen,
  MapPin,
  ArrowRight,
  HelpCircle,
  FileText,
  Award,
  ClipboardList,
  Globe,
  ExternalLink
} from "lucide-react";
import Link from "next/link";

interface Topic {
  id: number;
  milestone_id: number;
  title: string;
  description: string;
  resource_url?: string;
  is_completed: boolean;
}

interface Milestone {
  id: number;
  phase_number: number;
  title: string;
  description: string;
  estimated_weeks: number;
  topics: Topic[];
}

interface Roadmap {
  id: number;
  title: string;
  target_goal: string;
  job_readiness_score: number;
  milestones: Milestone[];
}

export default function RoadmapPage() {
  const { user, updateProfile } = useAuth();

  // Roadmap States
  const [roadmap, setRoadmap] = useState<Roadmap | null>(null);
  const [loading, setLoading] = useState(true);

  // Form input states
  const [careerGoal, setCareerGoal] = useState("Full-Stack Web Developer");
  const [skillLevel, setSkillLevel] = useState("Beginner");
  const [studyHours, setStudyHours] = useState(2.0);
  const [studyDuration, setStudyDuration] = useState("3 months");
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState("");

  // Selected topic for resource overlay
  const [selectedTopic, setSelectedTopic] = useState<Topic | null>(null);
  const [completingTopicId, setCompletingTopicId] = useState<number | null>(null);
  const [resources, setResources] = useState<any | null>(null);
  const [loadingResources, setLoadingResources] = useState(false);

  const fetchActiveRoadmap = async () => {
    try {
      const data = await apiFetch("/roadmaps/active");
      setRoadmap(data);
    } catch (e) {
      console.error("Failed to load active roadmap", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchActiveRoadmap();
  }, []);

  useEffect(() => {
    if (selectedTopic) {
      setResources(null);
      const fetchResources = async () => {
        setLoadingResources(true);
        try {
          const res = await apiFetch(`/roadmaps/topics/${selectedTopic.id}/resources`);
          setResources(res);
        } catch (e) {
          console.error("Failed to load topic resources", e);
        } finally {
          setLoadingResources(false);
        }
      };
      fetchResources();
    } else {
      setResources(null);
    }
  }, [selectedTopic]);

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setGenerating(true);

    const duration = studyDuration.trim();
    if (!duration) {
      setError("Study duration is required.");
      setGenerating(false);
      return;
    }

    const numberMatch = duration.match(/([+-]?\d+(?:\.\d+)?)/);
    if (!numberMatch) {
      setError("Study duration must contain a numeric value (e.g., '2 months', '90 days').");
      setGenerating(false);
      return;
    }

    const num = parseFloat(numberMatch[1]);
    if (num <= 0 || isNaN(num)) {
      setError("Study duration must be a valid positive value.");
      setGenerating(false);
      return;
    }

    const lowerDuration = duration.toLowerCase();
    const hasUnit = ["day", "week", "month", "year"].some(unit => lowerDuration.includes(unit));
    if (!hasUnit) {
      setError("Study duration must specify a unit (e.g., 'days', 'weeks', 'months', 'years').");
      setGenerating(false);
      return;
    }

    try {
      const data = await apiFetch("/roadmaps/generate", {
        method: "POST",
        body: JSON.stringify({
          career_goal: careerGoal,
          skill_level: skillLevel,
          daily_study_hours: studyHours,
          study_duration: duration
        })
      });
      setRoadmap(data);
      await updateProfile({
        career_goal: careerGoal,
        skill_level: skillLevel as "Beginner" | "Intermediate" | "Advanced",
        daily_study_hours: studyHours,
        study_duration: duration
      });
    } catch (err: any) {
      console.error("Generation failed", err);
      setError(err.message || "Failed to generate roadmap. Please check your inputs.");
    } finally {
      setGenerating(false);
    }
  };

  const handleCompleteTopic = async (topicId: number) => {
    setCompletingTopicId(topicId);
    try {
      await apiFetch(`/roadmaps/topics/${topicId}/complete`, { method: "POST" });
      if (roadmap) {
        const updatedMilestones = roadmap.milestones.map((milestone) => ({
          ...milestone,
          topics: milestone.topics.map((topic) =>
            topic.id === topicId ? { ...topic, is_completed: true } : topic
          )
        }));
        setRoadmap({ ...roadmap, milestones: updatedMilestones });
        if (selectedTopic && selectedTopic.id === topicId) {
          setSelectedTopic({ ...selectedTopic, is_completed: true });
        }
      }
    } catch (e) {
      console.error("Failed to complete topic", e);
    } finally {
      setCompletingTopicId(null);
    }
  };

  if (loading) {
    return (
      <div className="flex-1 p-8 flex flex-col justify-center items-center">
        <span className="w-8 h-8 rounded-full border-2 border-indigo-500/30 border-t-indigo-500 animate-spin mb-2" />
        <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold">Retrieving Learning Roadmap...</p>
      </div>
    );
  }

  if (!roadmap) {
    return (
      <div className="flex-1 p-6 md:p-10 max-w-4xl mx-auto w-full space-y-8 relative">
        <div className="absolute top-10 left-10 w-80 h-80 bg-indigo-500/5 rounded-full blur-3xl pointer-events-none" />

        <div className="space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-xs font-semibold text-indigo-400">
            <Sparkles className="w-3.5 h-3.5" />
            AI Adaptive Planner
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-white font-outfit">
            Configure Your Copilot
          </h1>
          <p className="text-gray-400 text-sm">
            Fill in your career details and learning preferences. Our AI will partition, sequence, and output a structured learning curriculum.
          </p>
        </div>

        <form onSubmit={handleGenerate} className="glass-card p-8 rounded-3xl border border-white/5 space-y-6 relative">
          {error && (
            <div className="p-3.5 rounded-xl bg-red-500/10 border border-red-500/20 text-xs font-medium text-red-400">
              {error}
            </div>
          )}
          <div className="grid sm:grid-cols-2 gap-6">
            <div className="sm:col-span-2">
              <label className="block text-xs font-bold text-gray-400 uppercase tracking-wider mb-2.5">
                What is your target career goal?
              </label>
              <input
                type="text"
                required
                value={careerGoal}
                onChange={(e) => setCareerGoal(e.target.value)}
                placeholder="e.g., Railway Ticket Collector, IAS Officer, Doctor, Graphic Designer, Software Engineer"
                className="w-full px-4 py-3 glass-input text-sm"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-gray-400 uppercase tracking-wider mb-2.5">
                Current Skill Level
              </label>
              <select
                required
                value={skillLevel}
                onChange={(e) => setSkillLevel(e.target.value)}
                className="w-full px-4 py-3.5 glass-input text-sm bg-black/40 text-white border-white/5 focus:border-indigo-500"
              >
                <option value="Beginner">Beginner</option>
                <option value="Intermediate">Intermediate</option>
                <option value="Advanced">Advanced</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold text-gray-400 uppercase tracking-wider mb-2.5">
                Daily Study Capacity
              </label>
              <select
                value={studyHours}
                onChange={(e) => setStudyHours(parseFloat(e.target.value))}
                className="w-full px-4 py-3.5 glass-input text-sm bg-black/40 text-white border-white/5 focus:border-indigo-500"
              >
                <option value="1.0">1 Hour / Day</option>
                <option value="2.0">2 Hours / Day (Recommended)</option>
                <option value="4.0">4 Hours / Day (Aggressive)</option>
                <option value="6.0">6 Hours / Day (Full-time boot)</option>
              </select>
            </div>

            <div className="sm:col-span-2">
              <label className="block text-xs font-bold text-gray-400 uppercase tracking-wider mb-2.5">
                Study Duration
              </label>
              <input
                type="text"
                required
                value={studyDuration}
                onChange={(e) => setStudyDuration(e.target.value)}
                placeholder="Enter duration (e.g., 2 months, 90 days, 1 year)"
                className="w-full px-4 py-3.5 glass-input text-sm text-gray-300"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={generating}
            className="w-full py-4 glow-button font-bold text-sm tracking-wide flex items-center justify-center gap-2 mt-4 disabled:opacity-50"
          >
            {generating ? (
              <>
                <span className="w-5 h-5 rounded-full border-2 border-white/30 border-t-white animate-spin" />
                Architecting Personalized Roadmap...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                Generate Learning Roadmap
              </>
            )}
          </button>
        </form>
      </div>
    );
  }

  // --- RENDERING ACTIVE ROADMAP TIMELINE ---
  const totalTopics = roadmap.milestones.reduce((sum, m) => sum + m.topics.length, 0);
  const completedTopics = roadmap.milestones.reduce(
    (sum, m) => sum + m.topics.filter((t) => t.is_completed).length,
    0
  );
  const progressPct = totalTopics > 0 ? Math.round((completedTopics / totalTopics) * 100) : 0;

  return (
    <div className="flex-1 p-6 md:p-10 max-w-7xl mx-auto w-full grid lg:grid-cols-12 gap-8 relative">
      <div className="absolute top-0 right-20 w-[500px] h-[500px] bg-indigo-500/5 rounded-full blur-[100px] pointer-events-none" />

      {/* Main Roadmap Timeline Column */}
      <div className="lg:col-span-8 space-y-8">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div className="space-y-1">
            <h1 className="text-3xl font-extrabold text-white font-outfit truncate max-w-lg">
              {roadmap.title}
            </h1>
            <p className="text-gray-400 text-sm flex items-center gap-2">
              <MapPin className="w-3.5 h-3.5 text-indigo-400" />
              Goal: {roadmap.target_goal}
            </p>
          </div>
          <div className="flex items-center gap-6 shrink-0">
            <div className="text-right space-y-1">
              <p className="text-[10px] font-bold uppercase tracking-wider text-gray-500">Readiness:</p>
              <p className="text-2xl font-extrabold text-indigo-400 font-outfit">{roadmap.job_readiness_score}%</p>
            </div>
            <div className="text-right space-y-1">
              <p className="text-[10px] font-bold uppercase tracking-wider text-gray-500">Progress:</p>
              <p className="text-2xl font-extrabold text-teal-400 font-outfit">{progressPct}%</p>
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="w-full h-1.5 rounded-full bg-white/5 overflow-hidden">
          <div
            className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-teal-500 transition-all duration-500"
            style={{ width: `${progressPct}%` }}
          />
        </div>

        {/* Milestones */}
        <div className="space-y-6">
          {roadmap.milestones.map((milestone) => {
            const milestoneCompleted = milestone.topics.every((t) => t.is_completed);
            return (
              <div
                key={milestone.id}
                className={`glass-card p-5 rounded-3xl border transition-all duration-300 ${
                  milestoneCompleted
                    ? "border-teal-500/20 bg-teal-500/[0.01]"
                    : "border-white/5"
                }`}
              >
                <div className="flex items-start gap-4 mb-4">
                  <div
                    className={`w-8 h-8 rounded-xl border flex items-center justify-center text-xs font-extrabold font-outfit shrink-0 mt-0.5 ${
                      milestoneCompleted
                        ? "bg-teal-500/10 border-teal-500/30 text-teal-400"
                        : "bg-indigo-500/10 border-indigo-500/30 text-indigo-400"
                    }`}
                  >
                    {milestone.phase_number}
                  </div>
                  <div className="flex-1">
                    <div className="flex flex-wrap items-center justify-between gap-3 mb-1">
                      <h2 className="text-base font-bold text-white font-outfit">{milestone.title}</h2>
                      <span className="text-[10px] font-bold text-gray-500 uppercase tracking-wider bg-white/[0.03] border border-white/5 px-2 py-0.5 rounded-md">
                        ~{milestone.estimated_weeks} weeks
                      </span>
                    </div>
                    <p className="text-xs text-gray-400 leading-relaxed">{milestone.description}</p>
                  </div>
                </div>

                {/* Topics Grid inside Phase */}
                <div className="grid sm:grid-cols-2 gap-4">
                  {milestone.topics.map((topic) => (
                    <button
                      key={topic.id}
                      onClick={() => setSelectedTopic(topic)}
                      className={`p-4 rounded-2xl border text-left flex items-start gap-3.5 transition-all duration-300 ${
                        selectedTopic?.id === topic.id
                          ? "bg-indigo-600/10 border-indigo-500/40 shadow-lg shadow-indigo-500/5"
                          : topic.is_completed
                          ? "bg-teal-500/[0.02] border-teal-500/20 hover:border-teal-500/30"
                          : "bg-white/[0.01] border-white/5 hover:border-white/10"
                      }`}
                    >
                      <div className="shrink-0 mt-0.5">
                        {topic.is_completed ? (
                          <CheckCircle className="w-5 h-5 text-teal-400 fill-teal-400/10" />
                        ) : (
                          <Circle className="w-5 h-5 text-gray-500" />
                        )}
                      </div>
                      <div className="flex-1 overflow-hidden">
                        <h4
                          className={`text-sm font-semibold truncate ${
                            topic.is_completed ? "text-gray-400 line-through" : "text-white"
                          }`}
                        >
                          {topic.title}
                        </h4>
                        <p className="text-xs text-gray-500 line-clamp-1 mt-1 font-medium">
                          {topic.description}
                        </p>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Right Column: Resource & Actions Panel */}
      <div className="lg:col-span-4">
        {selectedTopic ? (
          <div className="glass-card p-6 rounded-3xl border border-white/5 space-y-6 sticky top-6">
            {/* Topic Header */}
            <div className="space-y-2">
              <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-400 flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-indigo-400" /> Active Learning Module
              </span>
              <h3 className="text-xl font-bold text-white font-outfit leading-tight">
                {selectedTopic.title}
              </h3>
              <p className="text-gray-400 text-xs leading-relaxed">
                {selectedTopic.description}
              </p>
            </div>

            {/* Recommended Resources Panel */}
            <div className="border-t border-white/5 pt-4 space-y-4">
              <h4 className="text-xs font-bold uppercase tracking-wider text-indigo-400 flex items-center gap-1.5">
                <BookOpen className="w-3.5 h-3.5 text-indigo-400" /> Recommended Resources
              </h4>

              {loadingResources ? (
                <div className="py-8 flex flex-col items-center justify-center text-xs text-gray-500 uppercase tracking-wider font-semibold">
                  <span className="w-6 h-6 rounded-full border-2 border-indigo-500/20 border-t-indigo-500 animate-spin mb-2" />
                  Generating Study Assets...
                </div>
              ) : resources ? (
                <div className="space-y-5 max-h-[480px] overflow-y-auto pr-1">

                  {/* Card 1: AI Study Notes */}
                  <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/5 hover:border-indigo-500/20 transition-all duration-300 space-y-3">
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-xl bg-indigo-500/10 border border-indigo-500/25 text-indigo-400">
                        <FileText className="w-4 h-4" />
                      </div>
                      <div>
                        <h5 className="text-xs font-bold text-white uppercase tracking-wider">📖 AI Study Notes</h5>
                        <p className="text-[10px] text-gray-500">Concise revision summary and pitfalls</p>
                      </div>
                    </div>
                    {resources.notes && (
                      <div className="space-y-3 text-xs text-gray-300">
                        <div className="space-y-1.5">
                          <span className="font-bold text-indigo-300 text-[10px] uppercase tracking-wider block">Key Concepts</span>
                          <ul className="list-disc pl-4 space-y-1">
                            {resources.notes.key_concepts?.map((c: string, idx: number) => (
                              <li key={idx} className="leading-relaxed">{c}</li>
                            ))}
                          </ul>
                        </div>
                        <div className="space-y-1.5">
                          <span className="font-bold text-indigo-300 text-[10px] uppercase tracking-wider block">Important Points</span>
                          <ul className="list-disc pl-4 space-y-1">
                            {resources.notes.important_points?.map((p: string, idx: number) => (
                              <li key={idx} className="leading-relaxed">{p}</li>
                            ))}
                          </ul>
                        </div>
                        <div className="p-3 rounded-xl bg-white/[0.02] border border-white/5 space-y-1">
                          <span className="font-bold text-white text-[10px] uppercase tracking-wider block">Revision Summary</span>
                          <p className="text-[11px] leading-relaxed text-gray-400">{resources.notes.revision_summary}</p>
                        </div>
                        {resources.notes.common_mistakes && resources.notes.common_mistakes.length > 0 && (
                          <div className="p-3 rounded-xl bg-rose-500/5 border border-rose-500/10 space-y-1.5">
                            <span className="font-bold text-rose-400 text-[10px] uppercase tracking-wider block">Common Mistakes</span>
                            <ul className="list-disc pl-4 space-y-1 text-rose-300/80">
                              {resources.notes.common_mistakes.map((m: string, idx: number) => (
                                <li key={idx}>{m}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    )}
                  </div>

                  {/* Card 2: Practice Questions */}
                  <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/5 hover:border-indigo-500/20 transition-all duration-300 space-y-3">
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-xl bg-indigo-500/10 border border-indigo-500/25 text-indigo-400">
                        <HelpCircle className="w-4 h-4" />
                      </div>
                      <div>
                        <h5 className="text-xs font-bold text-white uppercase tracking-wider">🧩 Practice Questions</h5>
                        <p className="text-[10px] text-gray-500">Custom scenarios &amp; coding prompts</p>
                      </div>
                    </div>
                    {resources.questions && (
                      <div className="space-y-3">
                        {resources.questions.map((q: any, qIdx: number) => (
                          <QuestionCard key={qIdx} q={q} qIdx={qIdx} />
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Card 3: Official Resources */}
                  <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/5 hover:border-indigo-500/20 transition-all duration-300 space-y-3">
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-xl bg-indigo-500/10 border border-indigo-500/25 text-indigo-400">
                        <Globe className="w-4 h-4" />
                      </div>
                      <div>
                        <h5 className="text-xs font-bold text-white uppercase tracking-wider">🌐 Official Resources</h5>
                        <p className="text-[10px] text-gray-500">Government &amp; certification portals</p>
                      </div>
                    </div>
                    {resources.official_resources && (
                      <div className="space-y-3">
                        {resources.official_resources.map((res: any, rIdx: number) => (
                          <div key={rIdx} className="p-3 rounded-xl bg-black/30 border border-white/5 flex justify-between items-start gap-4 hover:border-indigo-500/20 transition-colors">
                            <div className="space-y-1">
                              <h6 className="text-xs font-bold text-white leading-snug">{res.name}</h6>
                              <p className="text-[10px] text-gray-400 leading-relaxed">{res.description}</p>
                            </div>
                            <a
                              href={res.link}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="p-1.5 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 hover:bg-indigo-500/20 transition-colors shrink-0"
                            >
                              <ExternalLink className="w-3.5 h-3.5" />
                            </a>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                </div>
              ) : (
                <div className="py-6 text-center text-xs text-gray-600 border border-dashed border-white/5 rounded-2xl bg-white/[0.01]">
                  Personalizing resources for {selectedTopic.title}...
                </div>
              )}
            </div>

            {/* Actions */}
            <div className="space-y-3 pt-2">
              {!selectedTopic.is_completed ? (
                <button
                  onClick={() => handleCompleteTopic(selectedTopic.id)}
                  disabled={completingTopicId !== null}
                  className="w-full py-3.5 glow-button text-sm font-semibold tracking-wide flex items-center justify-center gap-2"
                >
                  {completingTopicId === selectedTopic.id ? (
                    <span className="w-4 h-4 rounded-full border-2 border-white/30 border-t-white animate-spin" />
                  ) : (
                    <>
                      <CheckCircle className="w-4 h-4" />
                      Mark Module as Completed
                    </>
                  )}
                </button>
              ) : (
                <div className="py-3 px-4 rounded-xl bg-teal-500/10 border border-teal-500/20 text-center text-xs font-semibold text-teal-400 flex items-center justify-center gap-2">
                  <CheckCircle className="w-4 h-4 fill-teal-400/10" /> Finished Module
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="glass-card p-8 rounded-3xl border border-dashed border-white/5 text-center flex flex-col items-center justify-center h-[350px] sticky top-6 text-gray-500">
            <BookOpen className="w-10 h-10 text-gray-700 mb-3" />
            <h4 className="font-semibold text-sm text-gray-300">Select a Topic Module</h4>
            <p className="text-xs text-gray-600 max-w-[200px] mt-1.5 leading-relaxed">
              Click on any learning unit in the syllabus timeline to inspect resources, ask questions, or mark progress.
            </p>
          </div>
        )}
      </div>

    </div>
  );
}

function QuestionCard({ q, qIdx }: { q: any; qIdx: number }) {
  const [revealed, setRevealed] = useState(false);
  return (
    <div className="p-3.5 rounded-xl bg-white/[0.02] border border-white/5 space-y-2.5">
      <div className="flex justify-between items-start gap-3">
        <span className="text-[9px] font-bold text-indigo-400 uppercase bg-indigo-500/10 border border-indigo-500/20 px-1.5 py-0.5 rounded">
          {q.type}
        </span>
        <span className="text-[10px] text-gray-500 font-bold font-mono">Q{qIdx + 1}</span>
      </div>
      <p className="text-xs text-white leading-relaxed font-semibold">{q.question}</p>

      {q.options && q.options.length > 0 && (
        <div className="grid grid-cols-1 gap-2 pt-1">
          {q.options.map((opt: string, oIdx: number) => (
            <button
              key={oIdx}
              onClick={() => setRevealed(true)}
              className="w-full text-left px-3 py-2 rounded-lg bg-black/30 border border-white/5 text-[11px] text-gray-400 hover:border-white/10 transition-colors font-medium"
            >
              {opt}
            </button>
          ))}
        </div>
      )}

      {revealed ? (
        <div className="p-3 rounded-lg bg-indigo-500/5 border border-indigo-500/20 space-y-1 text-[11px]">
          <span className="font-bold text-white block">Answer: {q.correct_answer}</span>
          <p className="text-gray-400 leading-relaxed font-medium">{q.explanation}</p>
        </div>
      ) : (
        <button
          onClick={() => setRevealed(true)}
          className="text-[10px] text-indigo-400 font-bold hover:text-indigo-300 transition-colors pt-1 block"
        >
          Reveal Answer &amp; Explanation →
        </button>
      )}
    </div>
  );
}
