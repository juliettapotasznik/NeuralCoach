"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Label } from "@/components/ui/label"
import { Upload, Video, CheckCircle2, Loader2 } from "lucide-react"
import { apiClient, type AnalysisResponse } from "@/lib/api"
import { useToast } from "@/hooks/use-toast"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002"

export function VideoUpload() {
  const [file, setFile] = useState<File | null>(null)
  const [exerciseName, setExerciseName] = useState<string>("biceps")
  const [analyzing, setAnalyzing] = useState(false)
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null)
  const { toast } = useToast()

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
      setAnalysis(null)
    }
  }

  const handleAnalyze = async () => {
    if (!file) return

    setAnalyzing(true)

    try {
      const result = await apiClient.analyzeExercise(file, exerciseName)
      console.log("Analysis result:", result)
      console.log("Overlay video URL:", result.overlay_video_url)
      console.log("Processed video URL:", result.processed_video_url)
      setAnalysis(result)

      toast({
        title: "Analysis Complete",
        description: "Your exercise form has been analyzed successfully!",
      })
    } catch (error) {
      toast({
        title: "Analysis Failed",
        description: error instanceof Error ? error.message : "Failed to analyze video",
        variant: "destructive",
      })
    } finally {
      setAnalyzing(false)
    }
  }

  // Parse avg_rating from "94/100" format to number
  const getScoreFromRating = (rating?: string): number => {
    if (!rating) return 0
    if (typeof rating === "number") return rating
    const match = rating.match(/(\d+)/)
    return match ? parseInt(match[1]) : 0
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold mb-2">AI Form Analysis</h2>
        <p className="text-muted-foreground leading-relaxed">
          Upload a video of your exercise and get instant AI-powered feedback on your form
        </p>
      </div>

      {/* Exercise Selection */}
      {!analysis && (
        <div className="space-y-2">
          <Label htmlFor="exercise-select">Exercise Type</Label>
          <Select value={exerciseName} onValueChange={setExerciseName}>
            <SelectTrigger id="exercise-select">
              <SelectValue placeholder="Select exercise" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="biceps">Biceps Curls</SelectItem>
              <SelectItem value="squats">Squats</SelectItem>
              <SelectItem value="pushups">Push-ups</SelectItem>
              <SelectItem value="lunges">Lunges</SelectItem>
              <SelectItem value="plank">Plank</SelectItem>
            </SelectContent>
          </Select>
        </div>
      )}

      {/* Upload Area */}
      <div className="border-2 border-dashed border-border rounded-xl p-8 text-center hover:border-primary/50 transition-colors">
        <input type="file" accept="video/*" onChange={handleFileChange} className="hidden" id="video-upload" />
        <label htmlFor="video-upload" className="cursor-pointer">
          <div className="flex flex-col items-center gap-4">
            <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center">
              {file ? <Video className="h-8 w-8 text-primary" /> : <Upload className="h-8 w-8 text-primary" />}
            </div>
            <div>
              <p className="font-medium mb-1">{file ? file.name : "Click to upload or drag and drop"}</p>
              <p className="text-sm text-muted-foreground">MP4, MOV, or AVI (max 100MB)</p>
            </div>
          </div>
        </label>
      </div>

      {file && !analysis && (
        <Button
          onClick={handleAnalyze}
          disabled={analyzing}
          className="w-full bg-primary hover:bg-primary/90 text-primary-foreground"
          size="lg"
        >
          {analyzing ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Analyzing Form... This may take a moment
            </>
          ) : (
            "Analyze Form"
          )}
        </Button>
      )}

      {/* Analysis Results */}
      {analysis && (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4">
          <Card className="p-6 bg-primary/5 border-primary/20">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-xl font-semibold capitalize">{exerciseName}</h3>
                <p className="text-sm text-muted-foreground">Form Analysis Complete</p>
              </div>
              {analysis.avg_rating && (
                <div className="text-right">
                  <div className="text-3xl font-bold text-primary">{getScoreFromRating(analysis.avg_rating)}</div>
                  <div className="text-sm text-muted-foreground">Score</div>
                </div>
              )}
            </div>

            {/* Main Feedback */}
            <div className="space-y-3">
              <div className="flex items-start gap-3">
                <CheckCircle2 className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                <div className="text-sm leading-relaxed whitespace-pre-wrap">{analysis.feedback}</div>
              </div>
            </div>

            {/* Processing Time */}
            <div className="mt-4 pt-4 border-t border-border">
              <p className="text-xs text-muted-foreground">
                Processed in {analysis.processing_time.toFixed(2)}s
              </p>
            </div>
          </Card>

          {/* Overlay Video Display */}
          {(analysis.overlay_video_url || analysis.processed_video_url) && (() => {
            const videoUrl = `${API_BASE_URL}${analysis.overlay_video_url || analysis.processed_video_url}`;
            console.log("Video src URL:", videoUrl);
            console.log("API_BASE_URL:", API_BASE_URL);
            console.log("Video path:", analysis.overlay_video_url || analysis.processed_video_url);
            return (
              <Card className="p-6 glass-card">
                <h4 className="font-semibold mb-4">Form Analysis Video</h4>
                <div className="rounded-lg overflow-hidden bg-black">
                  <video
                    controls
                    className="w-full h-auto"
                    src={videoUrl}
                    onError={(e) => {
                      console.error("Video load error:", e);
                      console.error("Failed URL:", videoUrl);
                    }}
                  >
                    Your browser does not support the video tag.
                  </video>
                </div>
                <p className="text-xs text-muted-foreground mt-2">
                  Skeleton overlay showing detected pose and joint analysis
                </p>
              </Card>
            );
          })()}

          {/* Joint Ratings */}
          {analysis.joint_ratings && Object.keys(analysis.joint_ratings).length > 0 && (
            <Card className="p-6 glass-card">
              <h4 className="font-semibold mb-4">Joint Analysis</h4>
              <div className="space-y-3">
                {Object.entries(analysis.joint_ratings).map(([joint, rating]) => (
                  <div key={joint} className="space-y-1">
                    <div className="flex justify-between text-sm">
                      <span className="capitalize">{joint.replace(/_/g, " ")}</span>
                      <span className="font-medium">{rating}/100</span>
                    </div>
                    <div className="w-full bg-muted rounded-full h-2">
                      <div
                        className="bg-primary h-2 rounded-full transition-all"
                        style={{ width: `${rating}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          )}

          <Button
            onClick={() => {
              setFile(null)
              setAnalysis(null)
            }}
            variant="outline"
            className="w-full"
          >
            Analyze Another Video
          </Button>
        </div>
      )}
    </div>
  )
}
