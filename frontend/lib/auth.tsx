"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { apiFetch } from "./api";

interface UserProfile {
  career_goal: string;
  skill_level: "Beginner" | "Intermediate" | "Advanced";
  daily_study_hours: number;
  study_duration?: string;
  weak_areas: string[];
  strong_areas: string[];
}

interface User {
  id: number;
  email: string;
  name: string;
  streak: number;
  profile?: UserProfile;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name: string) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
  updateProfile: (profile: Partial<UserProfile>) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchCurrentUser = async () => {
    try {
      const data = await apiFetch("/users/me");
      setUser(data);
    } catch (e) {
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const token = localStorage.getItem("edumithra_token");
    if (token) {
      fetchCurrentUser();
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email: string, password: string) => {
    setLoading(true);
    try {
      const data = await apiFetch("/users/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      localStorage.setItem("edumithra_token", data.access_token);
      await fetchCurrentUser();
    } catch (error) {
      setLoading(false);
      throw error;
    }
  };

  const register = async (email: string, password: string, name: string) => {
    setLoading(true);
    try {
      const data = await apiFetch("/users/register", {
        method: "POST",
        body: JSON.stringify({ email, password, name }),
      });
      localStorage.setItem("edumithra_token", data.access_token);
      await fetchCurrentUser();
    } catch (error) {
      setLoading(false);
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem("edumithra_token");
    setUser(null);
    window.location.href = "/";
  };

  const updateProfile = async (profileData: Partial<UserProfile>) => {
    try {
      // Merge with existing profile data
      const currentProfile = user?.profile || {
        career_goal: "Full-Stack Web Developer",
        skill_level: "Beginner",
        daily_study_hours: 2.0,
        weak_areas: [],
        strong_areas: []
      };
      
      const payload = {
        ...currentProfile,
        ...profileData
      };

      const updatedProfile = await apiFetch("/users/profile", {
        method: "PUT",
        body: JSON.stringify(payload),
      });

      if (user) {
        setUser({
          ...user,
          profile: updatedProfile
        });
      }
    } catch (error) {
      console.error("Failed to update profile", error);
      throw error;
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        register,
        logout,
        refreshUser: fetchCurrentUser,
        updateProfile
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
// Fix typo in signatures: password: str -> password: string
