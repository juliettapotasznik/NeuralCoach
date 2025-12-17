"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Loader2, AlertCircle } from "lucide-react"
import { Checkbox } from "@/components/ui/checkbox"
import { DietPlanViewNew } from "./diet-plan-view-new"

interface UserProfile {
  age: number
  gender: string
  weight: number
  height: number
  goal: string
  activity_level: string
  diet: string | null
  intolerances: string | null  // String in UI, converted to array before sending
  time_frame: string
  prefer_ingredients: string[] | null
  num_meals: number
  macro_profile: string | null
}

interface DietPlanResult {
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
      ingredients?: string[]
      instructions?: string[]
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

export function DietQuestionnaire() {
  const [currentStep, setCurrentStep] = useState(0)
  const [submitting, setSubmitting] = useState(false)
  const [submitStatus, setSubmitStatus] = useState<"success" | "error" | null>(null)
  const [errorMessage, setErrorMessage] = useState("")
  const [dietPlanResult, setDietPlanResult] = useState<DietPlanResult | null>(null)

  const [profile, setProfile] = useState<Partial<UserProfile>>({
    time_frame: "day",
    diet: null,
    intolerances: null,
    prefer_ingredients: null,
    macro_profile: null,
  })

  const questions = [
    {
      id: 0,
      title: "Basic Information",
      description: "Tell us about yourself",
    },
    {
      id: 1,
      title: "Your Goal",
      description: "What do you want to achieve?",
    },
    {
      id: 2,
      title: "Activity Level",
      description: "How active are you?",
    },
    {
      id: 3,
      title: "Dietary Preferences",
      description: "Any dietary restrictions or preferences?",
    },
    {
      id: 4,
      title: "Meal Planning",
      description: "How many meals per day?",
    },
    {
      id: 5,
      title: "Plan Duration",
      description: "How long should your meal plan be?",
    },
  ]

  const currentQuestion = questions[currentStep]
  const isLastQuestion = currentStep === questions.length - 1

  const canProceed = () => {
    switch (currentStep) {
      case 0:
        return profile.age && profile.gender && profile.weight && profile.height
      case 1:
        return profile.goal
      case 2:
        return profile.activity_level
      case 3:
        return true // Diet preferences are optional
      case 4:
        return profile.num_meals
      case 5:
        return profile.time_frame // Plan duration
      default:
        return false
    }
  }

  const handleSubmit = async () => {
    setSubmitting(true)
    setSubmitStatus(null)
    setErrorMessage("")

    try {
      // Convert intolerances string to array
      const processedProfile = {
        ...profile,
        intolerances: profile.intolerances
          ? profile.intolerances.split(',').map(item => item.trim()).filter(item => item.length > 0)
          : null
      }

      // Use environment variable for API URL, fallback to localhost:8002
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002"
      const token = localStorage.getItem("access_token")
      const response = await fetch(`${apiUrl}/api/diet`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify(processedProfile),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.error || errorData.detail || `HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      console.log("Response from backend:", data)
      console.log("Request ID:", data.request_id)
      console.log("Nutrition:", data.nutrition)
      console.log("Meal Plan:", data.meal_plan)
      console.log("Cached:", data.cached)

      // Save to localStorage for dashboard display
      const dietPlanForDashboard = {
        nutrition: {
          calories: data.nutrition.target_calories,
          protein: data.meal_plan[0]?.daily_totals?.protein_g || 0,
          carbs: data.meal_plan[0]?.daily_totals?.carbs_g || 0,
          fat: data.meal_plan[0]?.daily_totals?.fat_g || 0,
        },
        meal_plan: data.meal_plan[0]?.meals?.map((meal: any) => ({
          meal_type: meal.meal_slot,
          recipes: [{ name: meal.recipe_name, calories: meal.calories }]
        })) || [],
        generated_at: new Date().toISOString()
      }
      localStorage.setItem("current_diet_plan", JSON.stringify(dietPlanForDashboard))

      setDietPlanResult(data)
      setSubmitStatus("success")
    } catch (error) {
      console.error("Error submitting profile:", error)
      setSubmitStatus("error")
      setErrorMessage(error instanceof Error ? error.message : "Failed to submit profile")
    } finally {
      setSubmitting(false)
    }
  }

  const handleNext = () => {
    if (isLastQuestion) {
      handleSubmit()
    } else {
      setCurrentStep(currentStep + 1)
    }
  }

  const handleReset = () => {
    setCurrentStep(0)
    setProfile({
      time_frame: "day",
      diet: null,
      intolerances: null,
      prefer_ingredients: null,
      macro_profile: null,
    })
    setSubmitStatus(null)
    setErrorMessage("")
    setDietPlanResult(null)
  }

  if (submitStatus === "success" && dietPlanResult) {
    return <DietPlanViewNew data={dietPlanResult} onCreateNew={handleReset} />
  }

  if (submitStatus === "error") {
    return (
      <div className="flex flex-col items-center justify-center py-20 space-y-4 animate-in fade-in">
        <div className="w-16 h-16 rounded-full bg-destructive/10 flex items-center justify-center">
          <AlertCircle className="h-10 w-10 text-destructive" />
        </div>
        <div className="text-center space-y-2">
          <h3 className="text-2xl font-semibold">Submission Failed</h3>
          <p className="text-muted-foreground">{errorMessage}</p>
          <p className="text-sm text-muted-foreground">Make sure your backend is running on port 8000</p>
        </div>
        <Button onClick={handleReset} variant="outline" className="mt-4 bg-transparent">
          Try Again
        </Button>
      </div>
    )
  }

  if (submitting) {
    return (
      <div className="flex flex-col items-center justify-center py-20 space-y-4">
        <Loader2 className="h-12 w-12 text-primary animate-spin" />
        <div className="text-center">
          <h3 className="text-xl font-semibold mb-2">Submitting Your Profile</h3>
          <p className="text-muted-foreground">Sending data to backend...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Progress */}
      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-muted-foreground">
            Step {currentStep + 1} of {questions.length}
          </span>
          <span className="text-primary font-medium">{Math.round(((currentStep + 1) / questions.length) * 100)}%</span>
        </div>
        <div className="h-2 bg-muted rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-primary to-accent transition-all duration-300"
            style={{ width: `${((currentStep + 1) / questions.length) * 100}%` }}
          />
        </div>
      </div>

      {/* Question Card */}
      <Card className="p-6 glass-card">
        <div className="mb-6">
          <h3 className="text-xl font-semibold mb-1">{currentQuestion.title}</h3>
          <p className="text-sm text-muted-foreground">{currentQuestion.description}</p>
        </div>

        {/* Step 0: Basic Information */}
        {currentStep === 0 && (
          <div className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="age">Age</Label>
                <Input
                  id="age"
                  type="number"
                  placeholder="25"
                  value={profile.age || ""}
                  onChange={(e) => setProfile({ ...profile, age: Number.parseInt(e.target.value) || 0 })}
                  className="bg-background"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="gender">Gender</Label>
                <div className="flex gap-2">
                  <Button
                    type="button"
                    variant={profile.gender === "male" ? "default" : "outline"}
                    className="flex-1"
                    onClick={() => setProfile({ ...profile, gender: "male" })}
                  >
                    Male
                  </Button>
                  <Button
                    type="button"
                    variant={profile.gender === "female" ? "default" : "outline"}
                    className="flex-1"
                    onClick={() => setProfile({ ...profile, gender: "female" })}
                  >
                    Female
                  </Button>
                </div>
              </div>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="weight">Weight (kg)</Label>
                <Input
                  id="weight"
                  type="number"
                  step="0.1"
                  placeholder="70"
                  value={profile.weight || ""}
                  onChange={(e) => setProfile({ ...profile, weight: Number.parseFloat(e.target.value) || 0 })}
                  className="bg-background"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="height">Height (cm)</Label>
                <Input
                  id="height"
                  type="number"
                  step="0.1"
                  placeholder="175"
                  value={profile.height || ""}
                  onChange={(e) => setProfile({ ...profile, height: Number.parseFloat(e.target.value) || 0 })}
                  className="bg-background"
                />
              </div>
            </div>
          </div>
        )}

        {/* Step 1: Goal */}
        {currentStep === 1 && (
          <div className="space-y-3">
            {["lose weight", "maintain", "gain weight"].map((goal) => (
              <div
                key={goal}
                className={`flex items-center space-x-3 p-4 rounded-lg border-2 transition-all cursor-pointer ${
                  profile.goal === goal
                    ? "border-primary bg-primary/5"
                    : "border-muted hover:border-primary/50 hover:bg-muted/50"
                }`}
                onClick={() => setProfile({ ...profile, goal })}
              >
                <Checkbox checked={profile.goal === goal} />
                <Label className="flex-1 cursor-pointer capitalize">{goal}</Label>
              </div>
            ))}
          </div>
        )}

        {/* Step 2: Activity Level */}
        {currentStep === 2 && (
          <div className="space-y-3">
            {["sedentary", "light", "moderate", "active", "very_active"].map((level) => (
              <div
                key={level}
                className={`flex items-center space-x-3 p-4 rounded-lg border-2 transition-all cursor-pointer ${
                  profile.activity_level === level
                    ? "border-primary bg-primary/5"
                    : "border-muted hover:border-primary/50 hover:bg-muted/50"
                }`}
                onClick={() => setProfile({ ...profile, activity_level: level })}
              >
                <Checkbox checked={profile.activity_level === level} />
                <Label className="flex-1 cursor-pointer capitalize">{level.replace("_", " ")}</Label>
              </div>
            ))}
          </div>
        )}

        {/* Step 3: Diet Preferences */}
        {currentStep === 3 && (
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>Dietary Restrictions (Optional)</Label>
              <div className="grid gap-2 sm:grid-cols-2">
                {[
                  "vegetarian",
                  "vegan",
                  "paleo",
                  "gluten-free",
                  "dairy-free",
                  "soy-free",
                  "nuts-free",
                  "eggs-free",
                  "shellfish-free",
                ].map((diet) => (
                  <div
                    key={diet}
                    className={`flex items-center space-x-3 p-3 rounded-lg border transition-all cursor-pointer ${
                      profile.diet === diet
                        ? "border-primary bg-primary/5"
                        : "border-muted hover:border-primary/50 hover:bg-muted/30"
                    }`}
                    onClick={() => setProfile({ ...profile, diet: profile.diet === diet ? null : diet })}
                  >
                    <Checkbox checked={profile.diet === diet} />
                    <Label className="flex-1 cursor-pointer capitalize text-sm">{diet}</Label>
                  </div>
                ))}
              </div>
            </div>

            

            <div className="space-y-2">
              <Label>Macro Profile (Optional)</Label>
              <div className="grid gap-2 sm:grid-cols-2">
                {["Balanced", "High-Fiber", "Low-Sodium", "Low-Carb", "Low-Fat", "High-Protein"].map((macro) => (
                  <div
                    key={macro}
                    className={`flex items-center space-x-3 p-3 rounded-lg border transition-all cursor-pointer ${
                      profile.macro_profile === macro
                        ? "border-accent bg-accent/5"
                        : "border-muted hover:border-accent/50 hover:bg-muted/30"
                    }`}
                    onClick={() =>
                      setProfile({ ...profile, macro_profile: profile.macro_profile === macro ? null : macro })
                    }
                  >
                    <Checkbox checked={profile.macro_profile === macro} />
                    <Label className="flex-1 cursor-pointer text-sm">{macro}</Label>
                  </div>
                ))}
              </div>
              <div className="space-y-2">
              <Label htmlFor="intolerances">Food Intolerances (Optional)</Label>
              <Input
                id="intolerances"
                type="text"
                placeholder="e.g., mushrooms, peanuts, lactose"
                value={profile.intolerances || ""}
                onChange={(e) => setProfile({ ...profile, intolerances: e.target.value || null })}
                className="bg-background"
              />
              <p className="text-xs text-muted-foreground">Separate multiple items with commas</p>
            </div>
            </div>

          </div>
        )}

        {/* Step 4: Number of Meals */}
        {currentStep === 4 && (
          <div className="space-y-3">
            {[3, 4, 5].map((num) => (
              <div
                key={num}
                className={`flex items-center space-x-3 p-4 rounded-lg border-2 transition-all cursor-pointer ${
                  profile.num_meals === num
                    ? "border-primary bg-primary/5"
                    : "border-muted hover:border-primary/50 hover:bg-muted/50"
                }`}
                onClick={() => setProfile({ ...profile, num_meals: num })}
              >
                <Checkbox checked={profile.num_meals === num} />
                <Label className="flex-1 cursor-pointer">{num} meals per day</Label>
              </div>
            ))}
          </div>
        )}

        {/* Step 5: Plan Duration */}
        {currentStep === 5 && (
          <div className="space-y-3">
            <div
              className={`flex items-center space-x-3 p-4 rounded-lg border-2 transition-all cursor-pointer ${
                profile.time_frame === "day"
                  ? "border-primary bg-primary/5"
                  : "border-muted hover:border-primary/50 hover:bg-muted/50"
              }`}
              onClick={() => setProfile({ ...profile, time_frame: "day" })}
            >
              <Checkbox checked={profile.time_frame === "day"} />
              <div className="flex-1">
                <Label className="cursor-pointer font-medium">1 Day Plan</Label>
                <p className="text-xs text-muted-foreground mt-1">Get a single day meal plan</p>
              </div>
            </div>
            <div
              className={`flex items-center space-x-3 p-4 rounded-lg border-2 transition-all cursor-pointer ${
                profile.time_frame === "week"
                  ? "border-primary bg-primary/5"
                  : "border-muted hover:border-primary/50 hover:bg-muted/50"
              }`}
              onClick={() => setProfile({ ...profile, time_frame: "week" })}
            >
              <Checkbox checked={profile.time_frame === "week"} />
              <div className="flex-1">
                <Label className="cursor-pointer font-medium">7 Day Plan (Week)</Label>
                <p className="text-xs text-muted-foreground mt-1">Get a complete week meal plan with varied meals</p>
              </div>
            </div>
          </div>
        )}
      </Card>

      {/* Navigation */}
      <div className="flex gap-4">
        {currentStep > 0 && (
          <Button onClick={() => setCurrentStep(currentStep - 1)} variant="outline" className="flex-1">
            Previous
          </Button>
        )}
        <Button
          onClick={handleNext}
          disabled={!canProceed()}
          className="flex-1 bg-primary hover:bg-primary/90 text-primary-foreground"
        >
          {isLastQuestion ? "Submit Profile" : "Next"}
        </Button>
      </div>
    </div>
  )
}
