"use client"

import { useMemo } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Activity, Beef, Wheat, Droplet, Flame, Download, RefreshCw, UtensilsCrossed } from "lucide-react"
import { MealCard } from "./meal-card"

interface BackendResponse {
  BMR: number
  target_calories: number
  message: string
  plan: string
}

interface Macros {
  protein: number
  protein_pct: number
  carbs: number
  carbs_pct: number
  fat: number
  fat_pct: number
}

interface Meal {
  meal_type: string
  title: string
  calories: number
  servings: number
  macros: Macros
  ingredients: string[]
  instructions: string[]
}

interface NutritionSummary {
  calories: number
  target_calories: number
  protein: number
  protein_pct: number
  carbs: number
  carbs_pct: number
  fat: number
  fat_pct: number
  target_protein_pct: number
  target_carbs_pct: number
  target_fat_pct: number
  macro_deviation: number
}

interface DietPlanViewProps {
  data: BackendResponse
  onCreateNew: () => void
}

function parsePlanText(
  planText: string,
  targetCalories: number,
): {
  nutrition_summary: NutritionSummary
  meals: Meal[]
} {
  const lines = planText.split("\n")

  // Parse nutrition summary
  let calories = 0
  let protein = 0
  let protein_pct = 0
  let carbs = 0
  let carbs_pct = 0
  let fat = 0
  let fat_pct = 0
  let target_protein_pct = 0
  let target_carbs_pct = 0
  let target_fat_pct = 0
  let macro_deviation = 0

  // Extract nutrition data
  for (const line of lines) {
    if (line.includes("Calories:")) {
      const match = line.match(/Calories:\s*(\d+)/)
      if (match) calories = Number.parseInt(match[1])
    }
    if (line.includes("Protein:")) {
      const match = line.match(/Protein:\s*([\d.]+)g\s*\(([\d.]+)%/)
      if (match) {
        protein = Number.parseFloat(match[1])
        protein_pct = Number.parseFloat(match[2])
      }
    }
    if (line.includes("Carbs:")) {
      const match = line.match(/Carbs:\s*([\d.]+)g\s*\(([\d.]+)%/)
      if (match) {
        carbs = Number.parseFloat(match[1])
        carbs_pct = Number.parseFloat(match[2])
      }
    }
    if (line.includes("Fat:")) {
      const match = line.match(/Fat:\s*([\d.]+)g\s*\(([\d.]+)%/)
      if (match) {
        fat = Number.parseFloat(match[1])
        fat_pct = Number.parseFloat(match[2])
      }
    }
    if (line.includes("TARGET MACROS:")) {
      const match = line.match(/P:(\d+)%\s*C:(\d+)%\s*F:(\d+)%/)
      if (match) {
        target_protein_pct = Number.parseInt(match[1])
        target_carbs_pct = Number.parseInt(match[2])
        target_fat_pct = Number.parseInt(match[3])
      }
    }
    if (line.includes("Macro Deviation:")) {
      const match = line.match(/Macro Deviation:\s*([\d.]+)%/)
      if (match) macro_deviation = Number.parseFloat(match[1])
    }
  }

  // Parse meals
  const meals: Meal[] = []
  const mealPattern = /🍽️\s+(\w+):\s+(.+)/g
  let match

  console.log("Looking for meals with pattern:", mealPattern)
  console.log("First 500 chars of plan:", planText.substring(0, 500))

  while ((match = mealPattern.exec(planText)) !== null) {
    console.log("Found meal match:", match)
    const mealType = match[1]
    const title = match[2]

    // Find the meal details in the following lines
    const mealStartIndex = planText.indexOf(match[0])
    const nextMealIndex = planText.indexOf("🍽️", mealStartIndex + 1)
    const mealSection =
      nextMealIndex > -1 ? planText.substring(mealStartIndex, nextMealIndex) : planText.substring(mealStartIndex)

    // Extract calories and servings
    const caloriesMatch = mealSection.match(/Calories:\s*(\d+)/)
    const servingsMatch = mealSection.match(/Servings:\s*(\d+)/)

    // Extract macros - note: using \( and \) to match literal parentheses
    const macrosMatch = mealSection.match(
      /Macros:\s*P:([\d.]+)g\s*\((\d+)%\)\s*\|\s*C:([\d.]+)g\s*\((\d+)%\)\s*\|\s*F:([\d.]+)g\s*\((\d+)%\)/,
    )

    console.log("Meal section:", mealSection.substring(0, 200))
    console.log("Calories match:", caloriesMatch)
    console.log("Servings match:", servingsMatch)
    console.log("Macros match:", macrosMatch)

    // Extract ingredients (they're in a JSON array format)
    const ingredientsMatch = mealSection.match(/Ingredients:\s*(\[.+?\])/)
    let ingredients: string[] = []
    if (ingredientsMatch) {
      try {
        // Handle truncated arrays
        let ingredientsStr = ingredientsMatch[1]
        if (!ingredientsStr.endsWith("]")) {
          ingredientsStr += '"]'
        }
        ingredients = JSON.parse(ingredientsStr)
      } catch (e) {
        ingredients = ["Ingredients not fully available"]
      }
    }

    // Extract instructions
    const instructionsMatch = mealSection.match(/Instructions:\s*(\[.+?\])/)
    let instructions: string[] = []
    if (instructionsMatch) {
      try {
        let instructionsStr = instructionsMatch[1]
        if (!instructionsStr.endsWith("]")) {
          instructionsStr += '"]'
        }
        instructions = JSON.parse(instructionsStr)
      } catch (e) {
        instructions = ["Instructions not fully available"]
      }
    }

    if (caloriesMatch && servingsMatch && macrosMatch) {
      meals.push({
        meal_type: mealType,
        title: title,
        calories: Number.parseInt(caloriesMatch[1]),
        servings: Number.parseInt(servingsMatch[1]),
        macros: {
          protein: Number.parseFloat(macrosMatch[1]),
          protein_pct: Number.parseInt(macrosMatch[2]),
          carbs: Number.parseFloat(macrosMatch[3]),
          carbs_pct: Number.parseInt(macrosMatch[4]),
          fat: Number.parseFloat(macrosMatch[5]),
          fat_pct: Number.parseInt(macrosMatch[6]),
        },
        ingredients,
        instructions,
      })
    }
  }

  return {
    nutrition_summary: {
      calories,
      target_calories: targetCalories,
      protein,
      protein_pct,
      carbs,
      carbs_pct,
      fat,
      fat_pct,
      target_protein_pct,
      target_carbs_pct,
      target_fat_pct,
      macro_deviation,
    },
    meals,
  }
}

export function DietPlanView({ data, onCreateNew }: DietPlanViewProps) {
  const parsedData = useMemo(() => {
    console.log("Raw plan text:", data.plan)
    const result = parsePlanText(data.plan, data.target_calories)
    console.log("Parsed meals:", result.meals)
    console.log("Number of meals found:", result.meals.length)
    return result
  }, [data.plan, data.target_calories])

  const { nutrition_summary, meals } = parsedData

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4">
      {/* Header Actions */}
      <div className="flex flex-wrap gap-3 justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold">Your Personalized Meal Plan</h2>
          <p className="text-sm text-muted-foreground">AI-generated nutrition plan optimized for your goals</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" className="gap-2 bg-transparent">
            <Download className="h-4 w-4" />
            Export
          </Button>
          <Button onClick={onCreateNew} size="sm" className="gap-2">
            <RefreshCw className="h-4 w-4" />
            Create New Plan
          </Button>
        </div>
      </div>

      {/* Nutrition Summary */}
      <Card className="p-6 glass-card border-primary/20">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center">
            <Activity className="h-6 w-6 text-white" />
          </div>
          <div>
            <h3 className="text-xl font-semibold">Nutrition Summary</h3>
            <p className="text-sm text-muted-foreground">Daily macro breakdown</p>
          </div>
        </div>

        {/* Calories */}
        <div className="mb-6 p-4 rounded-lg bg-gradient-to-r from-primary/10 to-accent/10 border border-primary/20">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <Flame className="h-5 w-5 text-primary" />
              <span className="font-semibold">Total Calories</span>
            </div>
            <div className="text-right">
              <span className="text-2xl font-bold text-primary">{nutrition_summary.calories}</span>
              <span className="text-muted-foreground"> / {nutrition_summary.target_calories}</span>
            </div>
          </div>
          <div className="h-2 bg-muted rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-primary to-accent transition-all"
              style={{
                width: `${Math.min((nutrition_summary.calories / nutrition_summary.target_calories) * 100, 100)}%`,
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
                  {nutrition_summary.protein.toFixed(1)}g
                  <span className="text-sm text-muted-foreground ml-1">
                    ({nutrition_summary.protein_pct.toFixed(1)}%)
                  </span>
                </div>
              </div>
            </div>
            <div className="space-y-1">
              <div className="h-2 bg-muted rounded-full overflow-hidden">
                <div
                  className="h-full bg-blue-500 transition-all"
                  style={{ width: `${nutrition_summary.protein_pct}%` }}
                />
              </div>
              <div className="text-xs text-muted-foreground">Target: {nutrition_summary.target_protein_pct}%</div>
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
                  {nutrition_summary.carbs.toFixed(1)}g
                  <span className="text-sm text-muted-foreground ml-1">
                    ({nutrition_summary.carbs_pct.toFixed(1)}%)
                  </span>
                </div>
              </div>
            </div>
            <div className="space-y-1">
              <div className="h-2 bg-muted rounded-full overflow-hidden">
                <div
                  className="h-full bg-amber-500 transition-all"
                  style={{ width: `${nutrition_summary.carbs_pct}%` }}
                />
              </div>
              <div className="text-xs text-muted-foreground">Target: {nutrition_summary.target_carbs_pct}%</div>
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
                  {nutrition_summary.fat.toFixed(1)}g
                  <span className="text-sm text-muted-foreground ml-1">({nutrition_summary.fat_pct.toFixed(1)}%)</span>
                </div>
              </div>
            </div>
            <div className="space-y-1">
              <div className="h-2 bg-muted rounded-full overflow-hidden">
                <div
                  className="h-full bg-emerald-500 transition-all"
                  style={{ width: `${nutrition_summary.fat_pct}%` }}
                />
              </div>
              <div className="text-xs text-muted-foreground">Target: {nutrition_summary.target_fat_pct}%</div>
            </div>
          </div>
        </div>

        {/* Macro Deviation */}
        <div className="flex items-center justify-center gap-2 p-3 rounded-lg bg-muted/50">
          <Activity className="h-4 w-4 text-primary" />
          <span className="text-sm">
            Macro Deviation:{" "}
            <span className="font-semibold text-primary">{nutrition_summary.macro_deviation.toFixed(1)}%</span>
          </span>
          <Badge variant="secondary" className="text-xs">
            {nutrition_summary.macro_deviation < 5 ? "Excellent" : "Good"}
          </Badge>
        </div>
      </Card>

      {/* Meals */}
      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <UtensilsCrossed className="h-5 w-5 text-primary" />
          <h3 className="text-xl font-semibold">Daily Meals</h3>
          <Badge variant="outline">{meals.length} meals</Badge>
        </div>

        {meals.map((meal, index) => (
          <MealCard key={index} meal={meal} />
        ))}
      </div>
    </div>
  )
}
