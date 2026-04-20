"use client"

import { useEffect, useState } from "react"
import { Navigation } from "@/components/navigation"
import { AchievementsCard } from "@/components/dashboard/achievements-card"
import { WorkoutTrackerCard } from "@/components/dashboard/workout-tracker-card"
import { TrainingPlanCard } from "@/components/dashboard/training-plan-card"
import { GoalTrackerCard } from "@/components/dashboard/goal-tracker-card"
import { DietOverviewCard } from "@/components/dashboard/diet-overview-card"
import { RecentPostsCard } from "@/components/dashboard/recent-posts-card"
import { UserStatsCard } from "@/components/dashboard/user-stats-card"
import { User } from "lucide-react"
import { apiClient } from "@/lib/api"

export default function DashboardPage() {
  const [username, setUsername] = useState<string>("")
  const [loading, setLoading] = useState(true)
  const [statsKey, setStatsKey] = useState(0)

  useEffect(() => {
    loadUser()
  }, [])

  const loadUser = async () => {
    try {
      const user = await apiClient.getCurrentUser()
      setUsername(user.username)
    } catch (err) {
      console.error("Failed to load user:", err)
    } finally {
      setLoading(false)
    }
  }

  const handlePointsEarned = () => {
    // Increment key to force re-render of UserStatsCard
    setStatsKey(prev => prev + 1)
  }

  return (
    <div className="min-h-screen">
      <Navigation />

      <div className="container mx-auto px-4 py-12">
        {/* Header */}
        <div className="mb-8 space-y-4">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-card border border-primary/20">
            <User className="h-4 w-4 text-primary" />
            <span className="text-sm font-medium">Personal Dashboard</span>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl md:text-5xl font-bold text-balance mb-2">
                Welcome back,{" "}
                <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                  {loading ? "..." : username}
                </span>!
              </h1>
              <p className="text-muted-foreground text-lg">Track your progress and stay motivated</p>
            </div>
          </div>
        </div>

        {/* Dashboard Grid */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {/* User Stats - Level and Points */}
          <div>
            <UserStatsCard key={statsKey} />
          </div>

          {/* Achievements - spans 2 columns on large screens */}
          <div className="lg:col-span-2">
            <AchievementsCard />
          </div>

          {/* Goal Tracker */}
          <div>
            <GoalTrackerCard onPointsEarned={handlePointsEarned} />
          </div>

          {/* Training Plan - spans 2 columns */}
          <div className="md:col-span-2">
            <TrainingPlanCard />
          </div>

          {/* Diet Overview */}
          <div>
            <DietOverviewCard />
          </div>

          {/* Recent Workouts */}
          <div className="md:col-span-2">
            <WorkoutTrackerCard />
          </div>

          {/* Recent Posts - spans full width */}
          <div className="md:col-span-2 lg:col-span-3">
            <RecentPostsCard onPointsEarned={handlePointsEarned} />
          </div>
        </div>
      </div>
    </div>
  )
}
