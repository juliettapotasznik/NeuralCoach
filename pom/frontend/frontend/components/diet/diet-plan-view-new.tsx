"use client"

import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Activity, Beef, Wheat, Droplet, Flame, Download, RefreshCw, UtensilsCrossed, Clock } from "lucide-react"

interface DietPlanData {
  nutrition: {
    bmi?: {
      bmi: number
      category: string
    }
    bmr?: number
    tdee?: number
    target_calories: number
    target_macros?: {
      protein_pct: number
      carbs_pct: number
      fat_pct: number
    }
  }
  meal_plan: Array<{
    day: number
    meals: Array<{
      meal_slot: string
      recipe_name: string
      calories: number
      protein_g: number
      carbs_g: number
      fat_g: number
      servings?: number
      ingredients?: string[] | string
      instructions?: string[] | string
    }>
    daily_totals: {
      calories: number
      protein_g: number
      carbs_g: number
      fat_g: number
    }
  }>
  generated_at: string
  cached: boolean
}

interface DietPlanViewNewProps {
  data: DietPlanData
  onCreateNew: () => void
}

export function DietPlanViewNew({ data, onCreateNew }: DietPlanViewNewProps) {
  const { nutrition, meal_plan, cached, generated_at } = data

  // Helper function to parse JSON strings
  const parseJsonString = (str: string | string[] | undefined): string[] => {
    if (!str) return []
    if (Array.isArray(str)) return str
    try {
      const parsed = JSON.parse(str)
      return Array.isArray(parsed) ? parsed : []
    } catch {
      return []
    }
  }

  // Calculate total macros across all days
  const totalMacros = meal_plan.reduce(
    (acc, day) => ({
      calories: acc.calories + day.daily_totals.calories,
      protein: acc.protein + day.daily_totals.protein_g,
      carbs: acc.carbs + day.daily_totals.carbs_g,
      fat: acc.fat + day.daily_totals.fat_g,
    }),
    { calories: 0, protein: 0, carbs: 0, fat: 0 }
  )

  // Average per day
  const avgPerDay = {
    calories: totalMacros.calories / meal_plan.length,
    protein: totalMacros.protein / meal_plan.length,
    carbs: totalMacros.carbs / meal_plan.length,
    fat: totalMacros.fat / meal_plan.length,
  }

  // Calculate macro percentages
  const caloriesFromMacros = avgPerDay.protein * 4 + avgPerDay.carbs * 4 + avgPerDay.fat * 9
  const proteinPct = ((avgPerDay.protein * 4) / caloriesFromMacros) * 100
  const carbsPct = ((avgPerDay.carbs * 4) / caloriesFromMacros) * 100
  const fatPct = ((avgPerDay.fat * 9) / caloriesFromMacros) * 100

  const handleExport = () => {
    const exportData = JSON.stringify(data, null, 2)
    const blob = new Blob([exportData], { type: "application/json" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `diet-plan-${new Date().toISOString().split("T")[0]}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4">
      {/* Header Actions */}
      <div className="flex flex-wrap gap-3 justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold">Your Personalized Meal Plan</h2>
          <p className="text-sm text-muted-foreground">
            AI-generated nutrition plan optimized for your goals
            {cached && <Badge variant="secondary" className="ml-2">Cached</Badge>}
          </p>
        </div>
        <div className="flex gap-2">
          <Button onClick={handleExport} variant="outline" size="sm" className="gap-2 bg-transparent">
            <Download className="h-4 w-4" />
            Export
          </Button>
          <Button onClick={onCreateNew} size="sm" className="gap-2">
            <RefreshCw className="h-4 w-4" />
            Create New Plan
          </Button>
        </div>
      </div>

      {/* Metadata */}
      <div className="flex gap-4 text-sm text-muted-foreground">
        <div className="flex items-center gap-1">
          <Clock className="h-4 w-4" />
          {new Date(generated_at).toLocaleString()}
        </div>
      </div>

      {/* BMI & TDEE Card */}
      {(nutrition.bmi || nutrition.bmr || nutrition.tdee) && (
        <Card className="p-6 glass-card border-accent/20">
          <h3 className="text-lg font-semibold mb-4">Your Metrics</h3>
          <div className="grid gap-4 md:grid-cols-3">
            {nutrition.bmi && (
              <div className="space-y-1">
                <div className="text-sm text-muted-foreground">BMI</div>
                <div className="text-2xl font-bold">{nutrition.bmi.bmi.toFixed(1)}</div>
                <Badge variant="outline">{nutrition.bmi.category}</Badge>
              </div>
            )}
            {nutrition.bmr && (
              <div className="space-y-1">
                <div className="text-sm text-muted-foreground">BMR</div>
                <div className="text-2xl font-bold">{Math.round(nutrition.bmr)}</div>
                <div className="text-xs text-muted-foreground">kcal/day at rest</div>
              </div>
            )}
            {nutrition.tdee && (
              <div className="space-y-1">
                <div className="text-sm text-muted-foreground">TDEE</div>
                <div className="text-2xl font-bold">{Math.round(nutrition.tdee)}</div>
                <div className="text-xs text-muted-foreground">kcal/day total</div>
              </div>
            )}
          </div>
        </Card>
      )}

      {/* Nutrition Summary */}
      <Card className="p-6 glass-card border-primary/20">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center">
            <Activity className="h-6 w-6 text-white" />
          </div>
          <div>
            <h3 className="text-xl font-semibold">Daily Nutrition Summary</h3>
            <p className="text-sm text-muted-foreground">Average macro breakdown per day</p>
          </div>
        </div>

        {/* Calories */}
        <div className="mb-6 p-4 rounded-lg bg-gradient-to-r from-primary/10 to-accent/10 border border-primary/20">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <Flame className="h-5 w-5 text-primary" />
              <span className="font-semibold">Average Daily Calories</span>
            </div>
            <div className="text-right">
              <span className="text-2xl font-bold text-primary">{Math.round(avgPerDay.calories)}</span>
              <span className="text-muted-foreground"> / {Math.round(nutrition.target_calories)}</span>
            </div>
          </div>
          <div className="h-2 bg-muted rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-primary to-accent transition-all"
              style={{
                width: `${Math.min((avgPerDay.calories / nutrition.target_calories) * 100, 100)}%`,
              }}
            />
          </div>
        </div>

        {/* Macros Grid */}
        <div className="grid gap-4 md:grid-cols-3 mb-4">
          {/* Protein */}
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center">
                <Beef className="h-4 w-4 text-blue-500" />
              </div>
              <div className="flex-1">
                <div className="text-sm text-muted-foreground">Protein</div>
                <div className="font-semibold">
                  {Math.round(avgPerDay.protein)}g
                  <span className="text-sm text-muted-foreground ml-1">({Math.round(proteinPct)}%)</span>
                </div>
              </div>
            </div>
            <div className="space-y-1">
              <div className="h-2 bg-muted rounded-full overflow-hidden">
                <div className="h-full bg-blue-500 transition-all" style={{ width: `${proteinPct}%` }} />
              </div>
              {nutrition.target_macros && (
                <div className="text-xs text-muted-foreground">Target: {Math.round(nutrition.target_macros.protein_pct)}%</div>
              )}
            </div>
          </div>

          {/* Carbs */}
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-amber-500/10 flex items-center justify-center">
                <Wheat className="h-4 w-4 text-amber-500" />
              </div>
              <div className="flex-1">
                <div className="text-sm text-muted-foreground">Carbs</div>
                <div className="font-semibold">
                  {Math.round(avgPerDay.carbs)}g
                  <span className="text-sm text-muted-foreground ml-1">({Math.round(carbsPct)}%)</span>
                </div>
              </div>
            </div>
            <div className="space-y-1">
              <div className="h-2 bg-muted rounded-full overflow-hidden">
                <div className="h-full bg-amber-500 transition-all" style={{ width: `${carbsPct}%` }} />
              </div>
              {nutrition.target_macros && (
                <div className="text-xs text-muted-foreground">Target: {Math.round(nutrition.target_macros.carbs_pct)}%</div>
              )}
            </div>
          </div>

          {/* Fat */}
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-emerald-500/10 flex items-center justify-center">
                <Droplet className="h-4 w-4 text-emerald-500" />
              </div>
              <div className="flex-1">
                <div className="text-sm text-muted-foreground">Fat</div>
                <div className="font-semibold">
                  {Math.round(avgPerDay.fat)}g
                  <span className="text-sm text-muted-foreground ml-1">({Math.round(fatPct)}%)</span>
                </div>
              </div>
            </div>
            <div className="space-y-1">
              <div className="h-2 bg-muted rounded-full overflow-hidden">
                <div className="h-full bg-emerald-500 transition-all" style={{ width: `${fatPct}%` }} />
              </div>
              {nutrition.target_macros && (
                <div className="text-xs text-muted-foreground">Target: {Math.round(nutrition.target_macros.fat_pct)}%</div>
              )}
            </div>
          </div>
        </div>
      </Card>

      {/* Meal Plan */}
      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <UtensilsCrossed className="h-5 w-5 text-primary" />
          <h3 className="text-xl font-semibold">
            {meal_plan.length > 1 ? `${meal_plan.length}-Day Meal Plan` : "Daily Meals"}
          </h3>
        </div>

        {meal_plan.map((day) => (
          <Card key={day.day} className="p-6 glass-card">
            <div className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <h4 className="text-lg font-semibold">Day {day.day}</h4>
                <Badge variant="outline">
                  {Math.round(day.daily_totals.calories)} kcal
                </Badge>
              </div>
              <div className="text-sm text-muted-foreground">
                P: {Math.round(day.daily_totals.protein_g)}g | C: {Math.round(day.daily_totals.carbs_g)}g | F: {Math.round(day.daily_totals.fat_g)}g
              </div>
            </div>

            <div className="space-y-4">
              {day.meals.map((meal, idx) => (
                <Card key={idx} className="p-4 bg-muted/50">
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <Badge variant="secondary" className="mb-2 capitalize">
                        {meal.meal_slot}
                      </Badge>
                      <h5 className="font-semibold">{meal.recipe_name}</h5>
                    </div>
                    <div className="text-right">
                      <div className="text-lg font-bold text-primary">{Math.round(meal.calories)} kcal</div>
                      {meal.servings && <div className="text-xs text-muted-foreground">{meal.servings} servings</div>}
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-2 text-sm mb-3">
                    <div>
                      <span className="text-muted-foreground">Protein:</span>
                      <span className="font-medium ml-1">{Math.round(meal.protein_g)}g</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Carbs:</span>
                      <span className="font-medium ml-1">{Math.round(meal.carbs_g)}g</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Fat:</span>
                      <span className="font-medium ml-1">{Math.round(meal.fat_g)}g</span>
                    </div>
                  </div>

                  {meal.ingredients && (
                    <details className="mt-3">
                      <summary className="cursor-pointer text-sm font-medium text-primary hover:underline">
                        View Ingredients & Instructions
                      </summary>
                      <div className="mt-3 space-y-3">
                        <div>
                          <div className="text-sm font-medium mb-1">Ingredients:</div>
                          <ul className="text-sm text-muted-foreground list-disc list-inside space-y-1">
                            {parseJsonString(meal.ingredients).map((ingredient, i) => (
                              <li key={i}>{ingredient}</li>
                            ))}
                          </ul>
                        </div>
                        {meal.instructions && (
                          <div>
                            <div className="text-sm font-medium mb-1">Instructions:</div>
                            <ol className="text-sm text-muted-foreground list-decimal list-inside space-y-1">
                              {parseJsonString(meal.instructions).map((instruction, i) => (
                                <li key={i}>{instruction}</li>
                              ))}
                            </ol>
                          </div>
                        )}
                      </div>
                    </details>
                  )}
                </Card>
              ))}
            </div>
          </Card>
        ))}
      </div>
    </div>
  )
}
