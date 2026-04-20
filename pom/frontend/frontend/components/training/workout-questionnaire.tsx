"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Checkbox } from "@/components/ui/checkbox"
import { Loader2, Sparkles, Calendar, Dumbbell, Target } from "lucide-react"
import { apiClient } from "@/lib/api"

const questions = [
  {
    id: "goal",
    question: "What is your primary fitness goal?",
    type: "radio",
    options: ["Build muscle", "Lose weight", "Improve flexibility", "Improve endurance", "Improve overall fitness"],
  },
  {
    id: "available_days_per_week",
    question: "How many days per week can you train?",
    type: "radio",
    options: ["1", "2", "3", "4", "5", "6", "7"],
  },
  {
    id: "training_location",
    question: "Where do you train?",
    type: "radio",
    options: ["Gym", "Home", "Both"],
  },
  {
    id: "experience_level",
    question: "What is your training experience level?",
    type: "radio",
    options: ["Beginner", "Intermediate", "Advanced"],
  },
  {
    id: "training_focus",
    question: "What areas do you want to focus on?",
    type: "radio",
    options: ["Full body", "Upper body", "Lower body", "Chest", "Back", "Legs", "Arms", "Shoulders", "Core"],
  },
]

export function WorkoutQuestionnaire() {
  const [currentStep, setCurrentStep] = useState(0)
  const [answers, setAnswers] = useState<Record<string, any>>({})
  const [generating, setGenerating] = useState(false)
  const [workoutPlan, setWorkoutPlan] = useState<any>(null)

  const currentQuestion = questions[currentStep]
  const isLastQuestion = currentStep === questions.length - 1

  const handleAnswer = (value: any) => {
    setAnswers({ ...answers, [currentQuestion.id]: value })
  }

  const handleNext = () => {
    if (isLastQuestion) {
      generateWorkoutPlan()
    } else {
      setCurrentStep(currentStep + 1)
    }
  }

  const generateWorkoutPlan = async () => {
    setGenerating(true)

    try {
      // Map frontend answers to generator format
      const userProfile = {
        goal: answers.goal?.toLowerCase().replace(/ /g, '_') || 'improve_overall_fitness',
        available_days_per_week: parseInt(answers.available_days_per_week) || 3,
        training_location: answers.training_location?.toLowerCase() || 'gym',
        experience_level: answers.experience_level?.toLowerCase() || 'beginner',
        training_focus: answers.training_focus?.toLowerCase().replace(/ /g, '_') || 'full_body',
        session_duration_max: 90, // Default 90 minutes
      }

      // Call the training plan generator
      const trainingPlanUrl = process.env.NEXT_PUBLIC_TRAINING_PLAN_URL || 'http://localhost:8004'
      const response = await fetch(`${trainingPlanUrl}/generate_plan`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userProfile),
      })

      if (!response.ok) {
        throw new Error('Failed to generate workout plan')
      }

      const data = await response.json()
      const generatedPlan = data.plan

      // Convert generator format to our database format
      const allExercises = generatedPlan.plan.flatMap((day: any, dayIndex: number) =>
        day.exercises.map((exercise: any) => ({
          name: exercise.exercise,
          sets: exercise.sets?.toString() || "3",
          reps: exercise.reps?.toString() || "10",
          rest: "60s", // Default rest time
          day: `Day ${dayIndex + 1}`,
          focus: day.focus,
        }))
      )

      // Save to database
      const savedPlan = await apiClient.createWorkoutPlan("Personalized Training Program", allExercises)

      // Prepare display structure
      const daysData = generatedPlan.plan.map((day: any, dayIndex: number) => ({
        day: `Day ${dayIndex + 1}`,
        focus: day.focus,
        exercises: day.exercises.map((exercise: any) => ({
          name: exercise.exercise,
          sets: `${exercise.sets}x${exercise.reps}`,
          rest: "60s",
        })),
      }))

      const planData = {
        id: savedPlan.plan_id,
        name: "Personalized Training Program",
        duration: `${generatedPlan.weeks} weeks`,
        days: daysData,
        notes: [
          "Warm up for 5-10 minutes before each session",
          "Focus on progressive overload - increase weight when you can complete all sets",
          "Rest 60 seconds between sets",
          "Stay hydrated and maintain proper nutrition",
        ],
      }

      setWorkoutPlan(planData)
    } catch (error) {
      console.error("Failed to generate workout plan:", error)
    } finally {
      setGenerating(false)
    }
  }

  const handleReset = () => {
    setCurrentStep(0)
    setAnswers({})
    setWorkoutPlan(null)
  }

  if (workoutPlan) {
    return (
      <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4">
        <div className="text-center space-y-2">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary">
            <Sparkles className="h-4 w-4" />
            <span className="text-sm font-medium">Plan Generated</span>
          </div>
          <h2 className="text-2xl font-bold">{workoutPlan.name}</h2>
          <p className="text-muted-foreground">Duration: {workoutPlan.duration}</p>
        </div>

        <div className="space-y-4">
          {workoutPlan.days.map((day: any, index: number) => (
            <Card key={index} className="p-6 glass-card">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                  <Calendar className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <h3 className="font-semibold">{day.day}</h3>
                  <p className="text-sm text-muted-foreground">{day.focus}</p>
                </div>
              </div>

              <div className="space-y-3">
                {day.exercises.map((exercise: any, exIndex: number) => (
                  <div key={exIndex} className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                    <div className="flex items-center gap-3">
                      <Dumbbell className="h-4 w-4 text-primary" />
                      <span className="font-medium">{exercise.name}</span>
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {exercise.sets} • Rest: {exercise.rest}
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          ))}
        </div>

        <Card className="p-6 bg-accent/10 border-accent/20">
          <div className="flex items-start gap-3 mb-3">
            <Target className="h-5 w-5 text-accent mt-0.5" />
            <h4 className="font-semibold">Important Notes</h4>
          </div>
          <ul className="space-y-2 ml-8">
            {workoutPlan.notes.map((note: string, index: number) => (
              <li key={index} className="text-sm leading-relaxed">
                {note}
              </li>
            ))}
          </ul>
        </Card>

        <Button onClick={handleReset} variant="outline" className="w-full bg-transparent">
          Create New Plan
        </Button>
      </div>
    )
  }

  if (generating) {
    return (
      <div className="flex flex-col items-center justify-center py-20 space-y-4">
        <Loader2 className="h-12 w-12 text-primary animate-spin" />
        <div className="text-center">
          <h3 className="text-xl font-semibold mb-2">Generating Your Workout Plan</h3>
          <p className="text-muted-foreground">Our AI is creating a personalized program for you...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold mb-2">Personalized Workout Plan</h2>
        <p className="text-muted-foreground leading-relaxed">
          Answer a few questions to get an AI-generated workout plan tailored to your goals
        </p>
      </div>

      {/* Progress */}
      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-muted-foreground">
            Question {currentStep + 1} of {questions.length}
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

      {/* Question */}
      <Card className="p-6 glass-card">
        <h3 className="text-lg font-semibold mb-4">{currentQuestion.question}</h3>

        {currentQuestion.type === "radio" && (
          <RadioGroup value={answers[currentQuestion.id]} onValueChange={handleAnswer} className="space-y-3">
            {currentQuestion.options.map((option) => (
              <div
                key={option}
                className="flex items-center space-x-3 p-3 rounded-lg hover:bg-muted/50 transition-colors"
              >
                <RadioGroupItem value={option} id={option} />
                <Label htmlFor={option} className="flex-1 cursor-pointer">
                  {option}
                </Label>
              </div>
            ))}
          </RadioGroup>
        )}

        {currentQuestion.type === "checkbox" && (
          <div className="space-y-3">
            {currentQuestion.options.map((option) => (
              <div
                key={option}
                className="flex items-center space-x-3 p-3 rounded-lg hover:bg-muted/50 transition-colors"
              >
                <Checkbox
                  id={option}
                  checked={answers[currentQuestion.id]?.includes(option)}
                  onCheckedChange={(checked) => {
                    const current = answers[currentQuestion.id] || []
                    if (checked) {
                      handleAnswer([...current, option])
                    } else {
                      handleAnswer(current.filter((item: string) => item !== option))
                    }
                  }}
                />
                <Label htmlFor={option} className="flex-1 cursor-pointer">
                  {option}
                </Label>
              </div>
            ))}
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
          disabled={!answers[currentQuestion.id]}
          className="flex-1 bg-primary hover:bg-primary/90 text-primary-foreground"
        >
          {isLastQuestion ? "Generate Plan" : "Next"}
        </Button>
      </div>
    </div>
  )
}
