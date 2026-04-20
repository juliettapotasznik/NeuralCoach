"use client"

import { useEffect, useState } from "react"
import { Card } from "@/components/ui/card"
import { Scale, TrendingDown, TrendingUp, Activity, Zap } from "lucide-react"
import { apiClient, UserStats } from "@/lib/api"

export function BodyMetricsCard() {
  const [stats, setStats] = useState<UserStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await apiClient.getUserStats()
      setStats(data)
    } catch (err) {
      console.error("Failed to fetch user stats:", err)
      setError(err instanceof Error ? err.message : "Failed to load stats")
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card className="p-6 glass-card h-full">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
          <Activity className="h-5 w-5 text-primary" />
        </div>
        <div>
          <h2 className="text-xl font-semibold">Fitness Stats</h2>
          <p className="text-sm text-muted-foreground">
            {loading ? "Loading..." : `Level ${stats?.level || 1}`}
          </p>
        </div>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-destructive/10 text-destructive rounded-lg text-sm">
          {error}
        </div>
      )}

      {loading ? (
        <div className="text-center py-8 text-muted-foreground">Loading stats...</div>
      ) : !stats ? (
        <div className="text-center py-8 text-muted-foreground">No stats available</div>
      ) : (
        <div className="space-y-6">
          {/* Metrics Grid */}
          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 rounded-lg bg-muted/30">
              <div className="flex items-center gap-2 mb-2">
                <Zap className="h-4 w-4 text-accent" />
                <span className="text-xs text-muted-foreground">Points</span>
              </div>
              <div className="text-2xl font-bold mb-1">{stats.points}</div>
              <div className="text-xs text-muted-foreground">Total earned</div>
            </div>

            <div className="p-4 rounded-lg bg-muted/30">
              <div className="flex items-center gap-2 mb-2">
                <Activity className="h-4 w-4 text-primary" />
                <span className="text-xs text-muted-foreground">Workouts</span>
              </div>
              <div className="text-2xl font-bold mb-1">{stats.total_workouts}</div>
              <div className="text-xs text-muted-foreground">All time</div>
            </div>

            <div className="p-4 rounded-lg bg-muted/30">
              <div className="flex items-center gap-2 mb-2">
                <TrendingUp className="h-4 w-4 text-green-500" />
                <span className="text-xs text-muted-foreground">This Week</span>
              </div>
              <div className="text-2xl font-bold mb-1">{stats.workouts_this_week}</div>
              <div className="text-xs text-muted-foreground">workouts</div>
            </div>

            <div className="p-4 rounded-lg bg-muted/30">
              <div className="flex items-center gap-2 mb-2">
                <Scale className="h-4 w-4 text-accent" />
                <span className="text-xs text-muted-foreground">This Month</span>
              </div>
              <div className="text-2xl font-bold mb-1">{stats.workouts_this_month}</div>
              <div className="text-xs text-muted-foreground">workouts</div>
            </div>
          </div>

          {/* Streak */}
          <div className="p-4 rounded-lg bg-gradient-to-r from-primary/10 to-accent/10 border border-primary/20">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm text-muted-foreground mb-1">Current Streak</div>
                <div className="text-3xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                  {stats.current_streak} days
                </div>
              </div>
              <div className="text-4xl">🔥</div>
            </div>
          </div>
        </div>
      )}
    </Card>
  )
}
