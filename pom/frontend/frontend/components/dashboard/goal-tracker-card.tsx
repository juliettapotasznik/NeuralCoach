"use client"

import { useEffect, useState } from "react"
import { Card } from "@/components/ui/card"
import { Target, Plus } from "lucide-react"
import { apiClient, Goal } from "@/lib/api"
import { Button } from "@/components/ui/button"
import { CreateGoalDialog } from "./create-goal-dialog"
import { useToast } from "@/hooks/use-toast"

interface GoalTrackerCardProps {
  onPointsEarned?: () => void
}

export function GoalTrackerCard({ onPointsEarned }: GoalTrackerCardProps = {}) {
  const [goals, setGoals] = useState<Goal[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [completingId, setCompletingId] = useState<number | null>(null)
  const { toast } = useToast()

  useEffect(() => {
    loadGoals()
  }, [])

  const loadGoals = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await apiClient.getGoals()
      // Filter out completed goals - show only active ones
      const activeGoals = data.filter((goal) => !goal.completed)
      setGoals(activeGoals)
    } catch (err) {
      console.error("Failed to fetch goals:", err)
      setError(err instanceof Error ? err.message : "Failed to load goals")
    } finally {
      setLoading(false)
    }
  }

  const handleGoalCreated = () => {
    loadGoals()
    // Notify parent component to refresh stats
    if (onPointsEarned) {
      onPointsEarned()
    }
  }

  const handleCompleteGoal = async (goalId: number) => {
    setCompletingId(goalId)
    try {
      const response = await apiClient.completeGoal(goalId)

      // Show success toast with points earned
      if (response.points_earned) {
        toast({
          title: "Goal Completed!",
          description: `+${response.points_earned} XP earned! You're now level ${response.level} with ${response.total_points} points.`,
        })
      }

      loadGoals()
      // Notify parent component to refresh stats
      if (onPointsEarned) {
        onPointsEarned()
      }
    } catch (err) {
      console.error("Failed to complete goal:", err)
      toast({
        title: "Error",
        description: err instanceof Error ? err.message : "Failed to complete goal",
        variant: "destructive",
      })
    } finally {
      setCompletingId(null)
    }
  }

  return (
    <Card className="p-6 glass-card h-full">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
            <Target className="h-5 w-5 text-primary" />
          </div>
          <div>
            <h2 className="text-xl font-semibold">Goals</h2>
            <p className="text-sm text-muted-foreground">
              {loading ? "Loading..." : `${goals.length} active goals`}
            </p>
          </div>
        </div>
        {!loading && (
          <Button size="sm" variant="outline" className="gap-2" onClick={() => setDialogOpen(true)}>
            <Plus className="h-4 w-4" />
            Add Goal
          </Button>
        )}
      </div>

      <CreateGoalDialog open={dialogOpen} onClose={() => setDialogOpen(false)} onSuccess={handleGoalCreated} />

      {error && (
        <div className="mb-4 p-3 bg-destructive/10 text-destructive rounded-lg text-sm">
          {error}
        </div>
      )}

      {loading ? (
        <div className="text-center py-8 text-muted-foreground">Loading goals...</div>
      ) : goals.length === 0 ? (
        <div className="text-center py-8 text-muted-foreground">
          No goals yet. Start by adding one!
        </div>
      ) : (
        <div className="space-y-6">
          {goals.map((goal) => {
            const isCompleting = completingId === goal.id

            return (
              <div key={goal.id} className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-medium text-sm">{goal.title}</span>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleCompleteGoal(goal.id)}
                    disabled={isCompleting}
                    className="h-7 text-xs"
                  >
                    {isCompleting ? "Marking..." : "Complete"}
                  </Button>
                </div>
                <div className="space-y-1">
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>
                      {goal.current_value} {goal.unit}
                    </span>
                    <span>
                      {goal.target_value} {goal.unit}
                    </span>
                  </div>
                  <div className="h-2 bg-muted rounded-full overflow-hidden">
                    <div
                      className="h-full transition-all bg-gradient-to-r from-primary to-accent"
                      style={{ width: `${Math.min(goal.progress_percentage, 100)}%` }}
                    />
                  </div>
                </div>
                {goal.deadline && (
                  <p className="text-xs text-muted-foreground">
                    Deadline: {new Date(goal.deadline).toLocaleDateString()}
                  </p>
                )}
              </div>
            )
          })}
        </div>
      )}
    </Card>
  )
}
