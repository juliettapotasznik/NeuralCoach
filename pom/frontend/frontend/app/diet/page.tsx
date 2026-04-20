import { Navigation } from "@/components/navigation"
import { DietQuestionnaire } from "@/components/diet/diet-questionnaire"
import { Card } from "@/components/ui/card"
import { UtensilsCrossed, Sparkles } from "lucide-react"

export default function DietPage() {
  return (
    <div className="min-h-screen">
      <Navigation />

      <div className="container mx-auto px-4 py-12">
        {/* Header */}
        <div className="text-center mb-12 space-y-4">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-card border border-primary/20">
            <UtensilsCrossed className="h-4 w-4 text-primary" />
            <span className="text-sm font-medium">AI Nutrition Planning</span>
          </div>

          <h1 className="text-4xl md:text-5xl font-bold text-balance">
            Personalized{" "}
            <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">Meal Plans</span>
          </h1>

          <p className="text-muted-foreground text-lg max-w-2xl mx-auto text-pretty leading-relaxed">
            Get AI-generated meal plans tailored to your goals, preferences, and lifestyle
          </p>
        </div>

        {/* Main Content */}
        <div className="max-w-4xl mx-auto">
          <Card className="p-6 md:p-8 glass-card">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center">
                <Sparkles className="h-5 w-5 text-accent" />
              </div>
              <div>
                <h2 className="text-xl font-semibold">Create Your Meal Plan</h2>
                <p className="text-sm text-muted-foreground">Answer a few questions to get started</p>
              </div>
            </div>

            <DietQuestionnaire />
          </Card>
        </div>
      </div>
    </div>
  )
}
