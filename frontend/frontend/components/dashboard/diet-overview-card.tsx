"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { UtensilsCrossed, ArrowRight, Calendar, Circle, CheckCircle2 } from "lucide-react"
import { apiClient, DietPlanResponse } from "@/lib/api"
import { useToast } from "@/hooks/use-toast"

interface CompletedMeal {
  meal_type: string
  recipe_index: number
  completed_at: string
}

interface NutritionConsumed {
  calories: number
  protein: number
  carbs: number
  fat: number
}

export function DietOverviewCard() {
  const [dietPlan, setDietPlan] = useState<DietPlanResponse | null>(null)
  const [completedMeals, setCompletedMeals] = useState<CompletedMeal[]>([])
  const [nutritionConsumed, setNutritionConsumed] = useState<NutritionConsumed>({
    calories: 0,
    protein: 0,
    carbs: 0,
    fat: 0,
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [completingMeal, setCompletingMeal] = useState<string | null>(null)
  const router = useRouter()
  const { toast } = useToast()

  useEffect(() => {
    loadDietPlan()
  }, [])

  const loadDietPlan = async () => {
    try {
      setLoading(true)
      setError(null)
      const plan = await apiClient.getCurrentDietPlan()
      setDietPlan(plan)

      // Load completed meals
      const completed = await apiClient.getCompletedMeals()
      setCompletedMeals(completed.completed_meals)
      setNutritionConsumed(completed.nutrition_consumed)
    } catch (err) {
      console.error("Failed to load diet plan:", err)
      setError(err instanceof Error ? err.message : "Failed to load diet plan")
      setDietPlan(null)
    } finally {
      setLoading(false)
    }
  }

  const handleMarkMealComplete = async (mealType: string, recipeIndex: number) => {
    const key = `${mealType}-${recipeIndex}`
    setCompletingMeal(key)

    try {
      const response = await apiClient.markMealComplete(mealType, recipeIndex)

      // Reload to get updated nutrition
      const completed = await apiClient.getCompletedMeals()
      setCompletedMeals(completed.completed_meals)
      setNutritionConsumed(completed.nutrition_consumed)

      // Show points earned notification
      if (response.points_earned) {
        toast({
          title: "Meal Completed!",
          description: `+${response.points_earned} XP earned! You're now level ${response.level} with ${response.total_points} points.`,
        })
      }
    } catch (err) {
      console.error("Failed to mark meal complete:", err)
      toast({
        title: "Error",
        description: "Failed to mark meal as complete",
        variant: "destructive",
      })
    } finally {
      setCompletingMeal(null)
    }
  }

  const isMealCompleted = (mealType: string, recipeIndex: number) => {
    return completedMeals.some(
      (m) => m.meal_type === mealType && m.recipe_index === recipeIndex
    )
  }

  if (loading) {
    return (
      <Card className="p-6 glass-card h-full">
        <div className="text-center py-8 text-muted-foreground">Loading...</div>
      </Card>
    )
  }

  if (!dietPlan) {
    return (
      <Card className="p-6 glass-card h-full flex flex-col">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center">
            <UtensilsCrossed className="h-5 w-5 text-accent" />
          </div>
          <div>
            <h2 className="text-xl font-semibold">Today's Nutrition</h2>
            <p className="text-sm text-muted-foreground">No diet plan generated</p>
          </div>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-destructive/10 text-destructive rounded-lg text-sm">
            {error}
          </div>
        )}

        <div className="flex-1 flex flex-col items-center justify-center py-8 text-center space-y-4">
          <div className="w-16 h-16 rounded-full bg-accent/10 flex items-center justify-center">
            <Calendar className="h-8 w-8 text-accent" />
          </div>
          <div>
            <h3 className="font-semibold mb-1">No Diet Plan Yet</h3>
            <p className="text-sm text-muted-foreground">
              Generate a personalized diet plan to see your nutrition goals
            </p>
          </div>
          <Button onClick={() => router.push("/diet")} className="gap-2">
            Generate Diet Plan
            <ArrowRight className="h-4 w-4" />
          </Button>
        </div>
      </Card>
    )
  }

  const { nutrition } = dietPlan
  const macros = [
    { name: "Protein", current: nutritionConsumed.protein, target: nutrition.protein, color: "bg-primary", unit: "g" },
    { name: "Carbs", current: nutritionConsumed.carbs, target: nutrition.carbs, color: "bg-accent", unit: "g" },
    { name: "Fats", current: nutritionConsumed.fat, target: nutrition.fat, color: "bg-chart-3", unit: "g" },
  ]

  const caloriesPercentage = nutrition.calories > 0 ? (nutritionConsumed.calories / nutrition.calories) * 100 : 0

  return (
    <Card className="p-6 glass-card h-full">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center">
            <UtensilsCrossed className="h-5 w-5 text-accent" />
          </div>
          <div>
            <h2 className="text-xl font-semibold">Today's Nutrition</h2>
            <p className="text-sm text-muted-foreground">Track your meals</p>
          </div>
        </div>
        <Button size="sm" variant="outline" onClick={() => router.push("/diet")}>
          Generate New Plan
        </Button>
      </div>

      {/* Calories */}
      <div className="mb-6 p-4 rounded-lg bg-primary/5 border border-primary/20">
        <div className="flex justify-between items-baseline mb-2">
          <span className="text-sm text-muted-foreground">Calories</span>
          <div className="text-right">
            <span className="text-2xl font-bold text-primary">{Math.round(nutritionConsumed.calories)}</span>
            <span className="text-sm text-muted-foreground"> / {nutrition.calories}</span>
          </div>
        </div>
        <div className="h-2 bg-muted rounded-full overflow-hidden">
          <div className="h-full bg-primary transition-all" style={{ width: `${Math.min(caloriesPercentage, 100)}%` }} />
        </div>
      </div>

      {/* Macros */}
      <div className="space-y-4 mb-6">
        {macros.map((macro) => (
          <div key={macro.name} className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="font-medium">{macro.name}</span>
              <span className="text-muted-foreground">
                {Math.round(macro.current)}
                {macro.unit} / {macro.target}
                {macro.unit}
              </span>
            </div>
            <div className="h-2 bg-muted rounded-full overflow-hidden">
              <div
                className={`h-full ${macro.color} transition-all`}
                style={{ width: `${macro.target > 0 ? Math.min((macro.current / macro.target) * 100, 100) : 0}%` }}
              />
            </div>
          </div>
        ))}
      </div>

      {/* Meal List - showing only incomplete meals */}
      <div className="mt-6 pt-6 border-t border-border/50">
        <p className="text-sm text-muted-foreground mb-3">Today's Meals</p>
        {dietPlan.meal_plan.every(meal =>
          meal.recipes?.every((_: any, idx: number) => isMealCompleted(meal.meal_type, idx))
        ) ? (
          <div className="text-center py-8 text-muted-foreground">
            <CheckCircle2 className="h-12 w-12 text-accent mx-auto mb-2" />
            <p className="font-semibold">All meals completed!</p>
            <p className="text-sm">Great job on completing today's nutrition plan.</p>
          </div>
        ) : (
          <div className="space-y-3 max-h-64 overflow-y-auto">
            {dietPlan.meal_plan.map((meal, mealIdx) => {
              // Filter out completed recipes
              const activeRecipes = meal.recipes?.filter((_: any, recipeIdx: number) =>
                !isMealCompleted(meal.meal_type, recipeIdx)
              ) || []

              // Skip meal type if no active recipes
              if (activeRecipes.length === 0) return null

              return (
                <div key={mealIdx}>
                  <h4 className="text-sm font-semibold capitalize mb-2">{meal.meal_type}</h4>
                  <div className="space-y-2 ml-2">
                    {meal.recipes?.map((recipe: any, recipeIdx: number) => {
                      const isCompleted = isMealCompleted(meal.meal_type, recipeIdx)
                      const isCompleting = completingMeal === `${meal.meal_type}-${recipeIdx}`

                      // Hide completed meals
                      if (isCompleted) return null

                      return (
                        <div
                          key={recipeIdx}
                          className="p-3 rounded-lg border text-sm transition-all bg-muted/30 border-border/50"
                        >
                          <div className="flex items-start justify-between gap-2">
                            <div className="flex items-start gap-2 flex-1">
                              <Circle className="h-4 w-4 text-muted-foreground mt-0.5 flex-shrink-0" />
                              <div className="flex-1">
                                <p className="font-medium">
                                  {recipe.recipe_name || recipe.name || recipe.title || "Unnamed recipe"}
                                </p>
                                <p className="text-xs text-muted-foreground mt-0.5">
                                  {(recipe.calories || recipe.calories_per_serving) && `${Math.round(recipe.calories || recipe.calories_per_serving)} cal`}
                                  {(recipe.protein || recipe.protein_g || recipe.protein_per_serving) && ` • ${Math.round(recipe.protein || recipe.protein_g || recipe.protein_per_serving)}g protein`}
                                </p>
                              </div>
                            </div>
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => handleMarkMealComplete(meal.meal_type, recipeIdx)}
                              disabled={isCompleting}
                              className="h-7 px-2 text-xs"
                            >
                              {isCompleting ? "..." : "Done"}
                            </Button>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </Card>
  )
}
