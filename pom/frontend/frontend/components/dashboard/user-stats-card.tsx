"use client"

import { useEffect, useState } from "react"
import { Card } from "@/components/ui/card"
import { Trophy, Star, Zap } from "lucide-react"
import { apiClient } from "@/lib/api"

interface UserStats {
  username: string
  level: number
  points: number
  current_streak: number
  workouts_this_week: number
  workouts_this_month: number
  total_workouts: number
}

export function UserStatsCard() {
  const [stats, setStats] = useState<UserStats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    try {
      setLoading(true)
      const data = await apiClient.getUserStats()
      setStats(data)
    } catch (err) {
      console.error("Failed to load user stats:", err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <Card className="p-6 glass-card h-full">
        <div className="text-center py-8 text-muted-foreground">Loading...</div>
      </Card>
    )
  }

  if (!stats) {
    return null
  }

  // Calculate progress to next level (100 points per level)
  const pointsForCurrentLevel = (stats.level - 1) * 100
  const pointsForNextLevel = stats.level * 100
  const progressInCurrentLevel = stats.points - pointsForCurrentLevel
  const progressPercentage = (progressInCurrentLevel / 100) * 100

  return (
    <Card className="p-6 glass-card h-full">
      <div className="space-y-6">
        {/* Level Display */}
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-br from-primary to-accent mb-3">
            <Trophy className="h-10 w-10 text-white" />
          </div>
          <h2 className="text-3xl font-bold mb-1">Level {stats.level}</h2>
          <p className="text-sm text-muted-foreground">{stats.points} Total Points</p>
        </div>

        {/* Progress to Next Level */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Next Level</span>
            <span className="font-medium text-primary">{progressInCurrentLevel} / 100 XP</span>
          </div>
          <div className="h-3 bg-muted rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-primary to-accent transition-all duration-500"
              style={{ width: `${progressPercentage}%` }}
            />
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 gap-4">
          <div className="p-4 rounded-lg bg-muted/30 border border-border/50">
            <div className="flex items-center gap-2 mb-1">
              <Zap className="h-4 w-4 text-orange-500" />
              <span className="text-sm text-muted-foreground">Streak</span>
            </div>
            <p className="text-2xl font-bold">{stats.current_streak}</p>
            <p className="text-xs text-muted-foreground">days</p>
          </div>

          <div className="p-4 rounded-lg bg-muted/30 border border-border/50">
            <div className="flex items-center gap-2 mb-1">
              <Star className="h-4 w-4 text-yellow-500" />
              <span className="text-sm text-muted-foreground">This Week</span>
            </div>
            <p className="text-2xl font-bold">{stats.workouts_this_week}</p>
            <p className="text-xs text-muted-foreground">workouts</p>
          </div>
        </div>

        {/* Point Earnings Info */}
        <div className="pt-4 border-t border-border/50">
          <h4 className="text-sm font-semibold mb-3">Earn Points</h4>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Create Post</span>
              <span className="font-medium text-primary">+5 XP</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Create Goal</span>
              <span className="font-medium text-primary">+10 XP</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Complete Exercise</span>
              <span className="font-medium text-primary">+10 XP</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Complete Meal</span>
              <span className="font-medium text-primary">+15 XP</span>
            </div>
          </div>
        </div>
      </div>
    </Card>
  )
}
