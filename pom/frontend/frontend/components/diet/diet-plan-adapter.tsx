"use client"

import { DietPlanView } from "./diet-plan-view"

interface BackendResponse {
  BMR: number
  target_calories: number
  plan: string
  message: string
}

interface DietPlanAdapterProps {
  backendData: BackendResponse
  onCreateNew: () => void
}

/**
 * Adapter component that converts backend text format to structured data
 * for the DietPlanView component
 */
export function DietPlanAdapter({ backendData, onCreateNew }: DietPlanAdapterProps) {
  const parsePlan = (planText: string) => {
    const lines = planText.split('\n')
    const meals: any[] = []

    // Parse nutrition summary from the header
    let actualCalories = backendData.target_calories
    let totalProtein = 0
    let totalCarbs = 0
    let totalFat = 0
    let targetProteinPct = 30
    let targetCarbsPct = 40
    let targetFatPct = 30
    let macroDeviation = 5

    // Extract nutrition summary
    for (const line of lines) {
      const caloriesMatch = line.match(/Calories:\s*(\d+\.?\d*)\s*\/\s*(\d+)/)
      if (caloriesMatch) {
        actualCalories = parseFloat(caloriesMatch[1])
      }

      const proteinMatch = line.match(/Protein:\s*(\d+\.?\d*)g\s*\((\d+\.?\d*)% of calories\)/)
      if (proteinMatch) {
        totalProtein = parseFloat(proteinMatch[1])
      }

      const carbsMatch = line.match(/Carbs:\s*(\d+\.?\d*)g\s*\((\d+\.?\d*)% of calories\)/)
      if (carbsMatch) {
        totalCarbs = parseFloat(carbsMatch[1])
      }

      const fatMatch = line.match(/Fat:\s*(\d+\.?\d*)g\s*\((\d+\.?\d*)% of calories\)/)
      if (fatMatch) {
        totalFat = parseFloat(fatMatch[1])
      }

      const targetMatch = line.match(/TARGET MACROS:\s*P:(\d+)%\s*C:(\d+)%\s*F:(\d+)%/)
      if (targetMatch) {
        targetProteinPct = parseInt(targetMatch[1])
        targetCarbsPct = parseInt(targetMatch[2])
        targetFatPct = parseInt(targetMatch[3])
      }

      const deviationMatch = line.match(/Macro Deviation:\s*(\d+\.?\d*)%/)
      if (deviationMatch) {
        macroDeviation = parseFloat(deviationMatch[1])
      }
    }

    // Parse individual meals
    let currentMeal: any = null
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i]

      // Detect meal headers like "🍽️  BREAKFAST: Grilled Chicken" or "🍽️  LUNCH: Recipe Name"
      const mealMatch = line.match(/🍽️\s+([A-Z]+):\s*(.+)/)
      if (mealMatch) {
        if (currentMeal) {
          meals.push(currentMeal)
        }

        const mealType = mealMatch[1].toLowerCase()
        const capitalizedType = mealType.charAt(0).toUpperCase() + mealType.slice(1)

        currentMeal = {
          meal_type: capitalizedType,
          title: mealMatch[2].trim(),
          calories: 0,
          servings: 1,
          macros: { protein: 0, protein_pct: 0, carbs: 0, carbs_pct: 0, fat: 0, fat_pct: 0 },
          ingredients: [],
          instructions: []
        }
        continue
      }

      if (!currentMeal) continue

      // Parse meal calories and servings
      const mealCalMatch = line.match(/Calories:\s*(\d+\.?\d*)\s*\|\s*Servings:\s*(\d+)/)
      if (mealCalMatch) {
        currentMeal.calories = parseFloat(mealCalMatch[1])
        currentMeal.servings = parseInt(mealCalMatch[2])
        continue
      }

      // Parse meal macros like "P:45.5g (40%) | C:60.2g (35%) | F:25.1g (25%)"
      const mealMacrosMatch = line.match(/P:(\d+\.?\d*)g\s*\((\d+)%\)\s*\|\s*C:(\d+\.?\d*)g\s*\((\d+)%\)\s*\|\s*F:(\d+\.?\d*)g\s*\((\d+)%\)/)
      if (mealMacrosMatch) {
        currentMeal.macros = {
          protein: parseFloat(mealMacrosMatch[1]),
          protein_pct: parseInt(mealMacrosMatch[2]),
          carbs: parseFloat(mealMacrosMatch[3]),
          carbs_pct: parseInt(mealMacrosMatch[4]),
          fat: parseFloat(mealMacrosMatch[5]),
          fat_pct: parseInt(mealMacrosMatch[6])
        }
        continue
      }

      // Parse ingredients line
      if (line.includes('Ingredients:')) {
        const ingredientsText = line.split('Ingredients:')[1]?.trim()
        if (ingredientsText) {
          // Split by common separators and clean up
          currentMeal.ingredients = ingredientsText
            .split(/[,;]/)
            .map(ing => ing.trim())
            .filter(ing => ing && ing.length > 2)
            .slice(0, 10) // Limit to first 10
        }
        continue
      }

      // Parse instructions line
      if (line.includes('Instructions:')) {
        const instructionsText = line.split('Instructions:')[1]?.trim()
        if (instructionsText) {
          // Split by periods or numbered steps
          const steps = instructionsText.split(/\.\s+|\d+\.\s*/).filter(s => s.trim().length > 10)
          currentMeal.instructions = steps.slice(0, 5) // Limit to 5 steps
        }
        continue
      }
    }

    // Add last meal
    if (currentMeal) {
      meals.push(currentMeal)
    }

    // If no meals were parsed, create fallback
    if (meals.length === 0) {
      const estimatedMeals = 3
      const caloriesPerMeal = Math.floor(actualCalories / estimatedMeals)

      for (let i = 0; i < estimatedMeals; i++) {
        meals.push({
          meal_type: i === 0 ? "Breakfast" : i === 1 ? "Lunch" : "Dinner",
          title: "See full plan details below",
          calories: caloriesPerMeal,
          servings: 1,
          macros: {
            protein: (caloriesPerMeal * (targetProteinPct / 100)) / 4,
            protein_pct: targetProteinPct,
            carbs: (caloriesPerMeal * (targetCarbsPct / 100)) / 4,
            carbs_pct: targetCarbsPct,
            fat: (caloriesPerMeal * (targetFatPct / 100)) / 9,
            fat_pct: targetFatPct
          },
          ingredients: ["Check the raw plan text for full details"],
          instructions: planText.split('\n').filter(l => l.trim()).slice(0, 3)
        })
      }
    }

    // Calculate percentages if missing
    const totalMacroCalories = totalProtein * 4 + totalCarbs * 4 + totalFat * 9
    let protein_pct, carbs_pct, fat_pct

    if (totalMacroCalories > 0) {
      protein_pct = ((totalProtein * 4) / totalMacroCalories) * 100
      carbs_pct = ((totalCarbs * 4) / totalMacroCalories) * 100
      fat_pct = ((totalFat * 9) / totalMacroCalories) * 100
    } else {
      protein_pct = targetProteinPct
      carbs_pct = targetCarbsPct
      fat_pct = targetFatPct
    }

    const nutrition_summary = {
      calories: actualCalories,
      target_calories: backendData.target_calories,
      protein: totalProtein,
      protein_pct: protein_pct,
      carbs: totalCarbs,
      carbs_pct: carbs_pct,
      fat: totalFat,
      fat_pct: fat_pct,
      target_protein_pct: targetProteinPct,
      target_carbs_pct: targetCarbsPct,
      target_fat_pct: targetFatPct,
      macro_deviation: macroDeviation
    }

    return {
      nutrition_summary,
      meals
    }
  }

  const structuredData = parsePlan(backendData.plan)

  // Debug logging
  console.log("=== ADAPTER DEBUG ===")
  console.log("Raw backend plan:", backendData.plan)
  console.log("Parsed meals count:", structuredData.meals.length)
  console.log("Parsed meals:", structuredData.meals)
  console.log("Nutrition summary:", structuredData.nutrition_summary)
  console.log("===================")

  return <DietPlanView data={structuredData} onCreateNew={onCreateNew} />
}
