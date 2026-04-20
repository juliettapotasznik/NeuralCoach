"use client"

import { useEffect, useState } from "react"
import { Card } from "@/components/ui/card"
import { Dumbbell, Clock } from "lucide-react"
import { apiClient, RecentWorkout } from "@/lib/api"
import { formatDistanceToNow } from "date-fns"

export function WorkoutTrackerCard() {
  const [workouts, setWorkouts] = useState<RecentWorkout[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  useEffect(() => {
    loadWorkouts()
  }, [])

  const loadWorkouts = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await apiClient.getRecentWorkouts(5)
      setWorkouts(data)
    } catch (err) {
      console.error("Failed to fetch workouts:", err)
      setError(err instanceof Error ? err.message : "Failed to load workouts")
    } finally {
      setLoading(false)
    }
  }

  const getRatingColor = (rating: number | null) => {
    if (!rating) return "text-muted-foreground"
    if (rating >= 8) return "text-green-500"
    if (rating >= 6) return "text-yellow-500"
    return "text-red-500"
  }

  const getRatingLabel = (rating: number | null) => {
    if (!rating) return "Not rated"
    if (rating >= 8) return "Excellent"
    if (rating >= 6) return "Good"
    return "Needs work"
  }

  return (
    <Card className="p-6 glass-card h-full">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
          <Dumbbell className="h-5 w-5 text-primary" />
        </div>
        <div>
          <h2 className="text-xl font-semibold">Recent Workouts</h2>
          <p className="text-sm text-muted-foreground">
            {loading ? "Loading..." : `${workouts.length} analyzed exercises`}
          </p>
        </div>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-destructive/10 text-destructive rounded-lg text-sm">
          {error}
        </div>
      )}

      {loading ? (
        <div className="text-center py-8 text-muted-foreground">Loading workouts...</div>
      ) : workouts.length === 0 ? (
        <div className="text-center py-8 text-muted-foreground">
          No workouts yet. Upload a video in AI Training to get started!
        </div>
      ) : (
        <div className="space-y-3">
          {workouts.map((workout) => (
            <div
              key={workout.id}
              className="p-4 rounded-lg bg-muted/30 border border-border/50"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 space-y-2">
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold">{workout.exercise_name}</h3>
                    {workout.avg_rating !== null && (
                      <span
                        className={`text-xs font-medium px-2 py-0.5 rounded-full ${getRatingColor(
                          workout.avg_rating
                        )} bg-current/10`}
                      >
                        {getRatingLabel(workout.avg_rating)}
                      </span>
                    )}
                  </div>

                  <div className="flex items-center gap-4 text-xs text-muted-foreground">
                    <div className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      <span>{formatDistanceToNow(new Date(workout.created_at), { addSuffix: true })}</span>
                    </div>
                    {workout.avg_rating !== null && (
                      <div>
                        Rating: <span className="font-medium">{workout.avg_rating.toFixed(1)}/10</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </Card>
  )
}
