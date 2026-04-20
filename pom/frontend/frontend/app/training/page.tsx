import { Navigation } from "@/components/navigation"
import { VideoUpload } from "@/components/training/video-upload"
import { WorkoutQuestionnaire } from "@/components/training/workout-questionnaire"
import { Card } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Brain, Video, Sparkles } from "lucide-react"

export default function TrainingPage() {
  return (
    <div className="min-h-screen">
      <Navigation />

      <div className="container mx-auto px-4 py-12">
        {/* Header */}
        <div className="text-center mb-12 space-y-4">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-card border border-primary/20">
            <Brain className="h-4 w-4 text-primary" />
            <span className="text-sm font-medium">AI Training Assistant</span>
          </div>

          <h1 className="text-4xl md:text-5xl font-bold text-balance">
            Your Personal{" "}
            <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">AI Coach</span>
          </h1>

          <p className="text-muted-foreground text-lg max-w-2xl mx-auto text-pretty leading-relaxed">
            Get AI-powered form analysis and personalized workout plans tailored to your goals
          </p>
        </div>

        {/* Main Content */}
        <Tabs defaultValue="form-check" className="max-w-5xl mx-auto">
          <TabsList className="grid w-full grid-cols-2 glass-card">
            <TabsTrigger value="form-check" className="gap-2">
              <Video className="h-4 w-4" />
              Form Check
            </TabsTrigger>
            <TabsTrigger value="workout-plan" className="gap-2">
              <Sparkles className="h-4 w-4" />
              Workout Plan
            </TabsTrigger>
          </TabsList>

          <TabsContent value="form-check" className="mt-6">
            <Card className="p-6 md:p-8 glass-card">
              <VideoUpload />
            </Card>
          </TabsContent>

          <TabsContent value="workout-plan" className="mt-6">
            <Card className="p-6 md:p-8 glass-card">
              <WorkoutQuestionnaire />
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
