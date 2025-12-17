"use client"

import { useEffect, useState } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Dumbbell, CheckCircle2, Circle, Calendar } from "lucide-react"
import { apiClient } from "@/lib/api"
import { useRouter } from "next/navigation"
import { useToast } from "@/hooks/use-toast"

interface WorkoutPlan {
  id: number
  plan_name: string
  exercises: Exercise[]
  generated_at: string
  is_active: boolean
}

interface Exercise {
  name: string
  sets?: number
  reps?: number
  duration?: string
  rest?: string
}

export function TrainingPlanCard() {
  const [workoutPlan, setWorkoutPlan] = useState<WorkoutPlan | null>(null)
  const [completedIndices, setCompletedIndices] = useState<number[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [completingId, setCompletingId] = useState<number | null>(null)
  const router = useRouter()
  const { toast } = useToast()

  useEffect(() => {
    loadWorkoutPlan()
  }, [])

  const loadWorkoutPlan = async () => {
    try {
      setLoading(true)
      setError(null)
      const plan = await apiClient.getCurrentWorkoutPlan()
      setWorkoutPlan(plan)

      // Load completed exercises
      const completed = await apiClient.getCompletedExercises(plan.id)
      setCompletedIndices(completed.completed_indices)
    } catch (err) {
      console.error("Failed to load workout plan:", err)
      setError(err instanceof Error ? err.message : "Failed to load workout plan")
      setWorkoutPlan(null)
    } finally {
      setLoading(false)
    }
  }

  const handleMarkComplete = async (exerciseIndex: number) => {
    if (!workoutPlan) return

    setCompletingId(exerciseIndex)
    try {
      const response = await apiClient.markExerciseComplete(workoutPlan.id, exerciseIndex)
      setCompletedIndices([...completedIndices, exerciseIndex])

      // Show points earned notification
      if (response.points_earned) {
        toast({
          title: "Exercise Completed!",
          description: `+${response.points_earned} XP earned! You're now level ${response.level} with ${response.total_points} points.`,
        })
      }
    } catch (err) {
      console.error("Failed to mark exercise complete:", err)
      toast({
        title: "Error",
        description: "Failed to mark exercise as complete",
        variant: "destructive",
      })
    } finally {
      setCompletingId(null)
    }
  }

  if (loading) {
    return (
      <Card className="p-6 glass-card h-full">
        <div className="text-center py-8 text-muted-foreground">Loading...</div>
      </Card>
    )
  }

  if (!workoutPlan) {
    return (
      <Card className="p-6 glass-card h-full flex flex-col">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
            <Dumbbell className="h-5 w-5 text-primary" />
          </div>
          <div>
            <h2 className="text-xl font-semibold">Training Plan</h2>
            <p className="text-sm text-muted-foreground">No plan generated</p>
          </div>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-destructive/10 text-destructive rounded-lg text-sm">
            {error}
          </div>
        )}

        <div className="flex-1 flex flex-col items-center justify-center py-8 text-center space-y-4">
          <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center">
            <Calendar className="h-8 w-8 text-primary" />
          </div>
          <div>
            <h3 className="font-semibold mb-1">No Training Plan Yet</h3>
            <p className="text-sm text-muted-foreground">
              Generate a personalized training plan to track your workouts
            </p>
          </div>
        </div>
      </Card>
    )
  }

  const completedCount = completedIndices.length
  const totalCount = workoutPlan.exercises.length
  const progressPercentage = totalCount > 0 ? (completedCount / totalCount) * 100 : 0

  // Filter out completed exercises
  const activeExercises = workoutPlan.exercises
    .map((exercise, index) => ({ exercise, originalIndex: index }))
    .filter(({ originalIndex }) => !completedIndices.includes(originalIndex))

  return (
    <Card className="p-6 glass-card h-full">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
            <Dumbbell className="h-5 w-5 text-primary" />
          </div>
          <div>
            <h2 className="text-xl font-semibold">{workoutPlan.plan_name}</h2>
            <p className="text-sm text-muted-foreground">
              {completedCount} of {totalCount} exercises completed today
            </p>
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-6">
        <div className="h-2 bg-muted rounded-full overflow-hidden">
          <div
            className="h-full bg-primary transition-all duration-500"
            style={{ width: `${progressPercentage}%` }}
          />
        </div>
      </div>

      {/* Exercise List - showing only active (not completed) exercises */}
      {activeExercises.length === 0 ? (
        <div className="text-center py-8 text-muted-foreground">
          <CheckCircle2 className="h-12 w-12 text-primary mx-auto mb-2" />
          <p className="font-semibold">All exercises completed!</p>
          <p className="text-sm">Great job on finishing today's workout.</p>
        </div>
      ) : (
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {activeExercises.map(({ exercise, originalIndex }) => {
            const isCompleting = completingId === originalIndex

            return (
              <div
                key={originalIndex}
                className="p-4 rounded-lg border transition-all bg-muted/30 border-border/50"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-start gap-3 flex-1">
                    <Circle className="h-5 w-5 text-muted-foreground mt-0.5 flex-shrink-0" />
                    <div className="flex-1">
                      <h3 className="font-semibold">
                        {exercise.name}
                      </h3>
                      <div className="text-sm text-muted-foreground mt-1">
                        {exercise.sets && exercise.reps && (
                          <span>
                            {exercise.sets} sets × {exercise.reps} reps
                          </span>
                        )}
                        {exercise.duration && <span>{exercise.duration}</span>}
                        {exercise.rest && (
                          <span className="ml-2">• Rest: {exercise.rest}</span>
                        )}
                      </div>
                    </div>
                  </div>

                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleMarkComplete(originalIndex)}
                    disabled={isCompleting}
                  >
                    {isCompleting ? "Marking..." : "Complete"}
                  </Button>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </Card>
  )
}
