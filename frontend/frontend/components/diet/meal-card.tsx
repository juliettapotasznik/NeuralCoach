"use client"

import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Flame, Beef, Wheat, Droplet, Users, ChefHat, Clock } from "lucide-react"

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

interface MealCardProps {
  meal: Meal
}

export function MealCard({ meal }: MealCardProps) {
  const getMealIcon = (mealType: string) => {
    switch (mealType.toLowerCase()) {
      case "breakfast":
        return "🌅"
      case "lunch":
        return "☀️"
      case "dinner":
        return "🌙"
      case "snack":
        return "🍎"
      default:
        return "🍽️"
    }
  }

  const getMealColor = (mealType: string) => {
    switch (mealType.toLowerCase()) {
      case "breakfast":
        return "from-orange-400 to-yellow-400"
      case "lunch":
        return "from-blue-400 to-cyan-400"
      case "dinner":
        return "from-purple-400 to-pink-400"
      case "snack":
        return "from-green-400 to-emerald-400"
      default:
        return "from-primary to-accent"
    }
  }

  return (
    <Card className="overflow-hidden glass-card border-primary/10 hover:border-primary/30 transition-all">
      {/* Meal Header */}
      <div className="p-6">
        <div className="flex items-start gap-4 mb-4">
          {/* Meal Icon */}
          <div
            className={`w-14 h-14 rounded-xl bg-gradient-to-br ${getMealColor(meal.meal_type)} flex items-center justify-center text-3xl flex-shrink-0 shadow-lg`}
          >
            {getMealIcon(meal.meal_type)}
          </div>

          {/* Meal Info */}
          <div className="flex-1 min-w-0">
            <Badge variant="outline" className="mb-2 text-xs font-semibold">
              {meal.meal_type}
            </Badge>
            <h4 className="font-bold text-xl leading-tight text-balance mb-3">{meal.title}</h4>

            {/* Quick Stats */}
            <div className="flex flex-wrap gap-3 text-sm">
              <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-primary/10">
                <Flame className="h-4 w-4 text-primary" />
                <span className="font-semibold">{meal.calories} cal</span>
              </div>
              <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-muted">
                <Users className="h-4 w-4" />
                <span className="font-medium">
                  {meal.servings} serving{meal.servings > 1 ? "s" : ""}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Macros Breakdown */}
        <div className="mb-4 p-4 rounded-lg bg-gradient-to-r from-primary/5 to-accent/5 border border-primary/10">
          <div className="grid grid-cols-3 gap-3 mb-3">
            <div className="text-center">
              <div className="flex items-center justify-center gap-1 mb-1">
                <Beef className="h-3.5 w-3.5 text-blue-500" />
                <span className="text-xs text-muted-foreground">Protein</span>
              </div>
              <div className="font-bold text-blue-500">{meal.macros.protein.toFixed(1)}g</div>
              <div className="text-xs text-muted-foreground">{meal.macros.protein_pct}%</div>
            </div>
            <div className="text-center">
              <div className="flex items-center justify-center gap-1 mb-1">
                <Wheat className="h-3.5 w-3.5 text-amber-500" />
                <span className="text-xs text-muted-foreground">Carbs</span>
              </div>
              <div className="font-bold text-amber-500">{meal.macros.carbs.toFixed(1)}g</div>
              <div className="text-xs text-muted-foreground">{meal.macros.carbs_pct}%</div>
            </div>
            <div className="text-center">
              <div className="flex items-center justify-center gap-1 mb-1">
                <Droplet className="h-3.5 w-3.5 text-emerald-500" />
                <span className="text-xs text-muted-foreground">Fat</span>
              </div>
              <div className="font-bold text-emerald-500">{meal.macros.fat.toFixed(1)}g</div>
              <div className="text-xs text-muted-foreground">{meal.macros.fat_pct}%</div>
            </div>
          </div>

          {/* Macro Bars */}
          <div className="flex gap-1 h-2 rounded-full overflow-hidden">
            <div
              className="bg-blue-500"
              style={{ width: `${meal.macros.protein_pct}%` }}
              title={`Protein: ${meal.macros.protein_pct}%`}
            />
            <div
              className="bg-amber-500"
              style={{ width: `${meal.macros.carbs_pct}%` }}
              title={`Carbs: ${meal.macros.carbs_pct}%`}
            />
            <div
              className="bg-emerald-500"
              style={{ width: `${meal.macros.fat_pct}%` }}
              title={`Fat: ${meal.macros.fat_pct}%`}
            />
          </div>
        </div>

        {/* Ingredients */}
        <div className="mb-4">
          <div className="flex items-center gap-2 mb-3">
            <ChefHat className="h-4 w-4 text-primary" />
            <h5 className="font-semibold text-sm">Ingredients</h5>
          </div>
          <ul className="space-y-1.5 text-sm">
            {meal.ingredients.map((ingredient, i) => (
              <li key={i} className="flex items-start gap-2">
                <span className="text-primary mt-1 font-bold">•</span>
                <span className="text-muted-foreground leading-relaxed">{ingredient}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Instructions */}
        <div>
          <div className="flex items-center gap-2 mb-3">
            <Clock className="h-4 w-4 text-primary" />
            <h5 className="font-semibold text-sm">Instructions</h5>
          </div>
          <ol className="space-y-2.5 text-sm">
            {meal.instructions.map((instruction, i) => (
              <li key={i} className="flex items-start gap-3">
                <span className="flex-shrink-0 w-6 h-6 rounded-full bg-primary/10 text-primary flex items-center justify-center text-xs font-bold">
                  {i + 1}
                </span>
                <span className="text-muted-foreground pt-0.5 leading-relaxed">{instruction}</span>
              </li>
            ))}
          </ol>
        </div>
      </div>
    </Card>
  )
}
