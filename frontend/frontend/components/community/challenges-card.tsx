"use client"

import { useEffect, useState } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Target, Users, Calendar, Trophy, Flame, Dumbbell, LucideIcon, Plus, Minus } from "lucide-react"
import { apiClient, Challenge } from "@/lib/api"
import { CreateChallengeDialog } from "./create-challenge-dialog"
import { useToast } from "@/hooks/use-toast"

const iconMap: Record<string, LucideIcon> = {
  Flame: Flame,
  Dumbbell: Dumbbell,
  Target: Target,
}

export function ChallengesCard() {
  const [challenges, setChallenges] = useState<Challenge[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [joiningId, setJoiningId] = useState<number | null>(null)
  const [updatingId, setUpdatingId] = useState<number | null>(null)
  const { toast } = useToast()

  const fetchChallenges = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await apiClient.getChallenges()
      setChallenges(data)
    } catch (err) {
      console.error("Failed to fetch challenges:", err)
      setError(err instanceof Error ? err.message : "Failed to load challenges")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchChallenges()
  }, [])

  const handleJoinChallenge = async (challengeId: number) => {
    try {
      setJoiningId(challengeId)
      const response = await apiClient.joinChallenge(challengeId)

      // Show success toast with points earned
      if (response.points_earned) {
        toast({
          title: "Challenge Joined!",
          description: `+${response.points_earned} XP earned! You're now level ${response.level} with ${response.total_points} points.`,
        })
      } else {
        toast({
          title: "Challenge Joined!",
          description: "You've successfully joined the challenge.",
        })
      }

      await fetchChallenges()
    } catch (err) {
      console.error("Failed to join challenge:", err)
      toast({
        title: "Error",
        description: err instanceof Error ? err.message : "Failed to join challenge",
        variant: "destructive",
      })
    } finally {
      setJoiningId(null)
    }
  }

  const handleUpdateProgress = async (challengeId: number, currentProgress: number, increment: number) => {
    try {
      setUpdatingId(challengeId)
      const newProgress = Math.max(0, currentProgress + increment)
      const response = await apiClient.updateChallengeProgress(challengeId, newProgress)

      if (response.completed) {
        toast({
          title: "Challenge Completed!",
          description: "Congratulations on completing this challenge!",
        })
      } else {
        toast({
          title: "Progress Updated!",
          description: `Progress: ${response.progress}`,
        })
      }

      await fetchChallenges()
    } catch (err) {
      console.error("Failed to update challenge progress:", err)
      toast({
        title: "Error",
        description: err instanceof Error ? err.message : "Failed to update progress",
        variant: "destructive",
      })
    } finally {
      setUpdatingId(null)
    }
  }

  return (
    <Card className="p-6 glass-card">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
            <Target className="h-5 w-5 text-primary" />
          </div>
          <div>
            <h2 className="text-xl font-semibold">Active Challenges</h2>
            <p className="text-sm text-muted-foreground">Compete and earn rewards</p>
          </div>
        </div>
        <CreateChallengeDialog onSuccess={fetchChallenges} />
      </div>

      {error && (
        <div className="mb-4 p-3 bg-destructive/10 text-destructive rounded-lg text-sm">
          {error}
        </div>
      )}

      {loading ? (
        <div className="text-center py-8 text-muted-foreground">Loading challenges...</div>
      ) : challenges.length === 0 ? (
        <div className="text-center py-8 text-muted-foreground">
          No active challenges available
        </div>
      ) : (
        <div className="space-y-4">
          {challenges.map((challenge) => {
            const Icon = iconMap[challenge.icon] || Target
            return (
              <div
                key={challenge.id}
                className={`p-5 rounded-lg border transition-all ${
                  challenge.joined
                    ? "bg-primary/5 border-primary/20 hover:border-primary/40"
                    : "bg-muted/30 border-border/50 hover:border-border"
                }`}
              >
                <div className="flex items-start gap-4">
                  <div
                    className={`w-12 h-12 rounded-lg flex items-center justify-center flex-shrink-0 ${
                      challenge.joined ? "bg-primary/20" : "bg-muted"
                    }`}
                  >
                    <Icon className={`h-6 w-6 ${challenge.joined ? "text-primary" : "text-muted-foreground"}`} />
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-4 mb-2">
                      <div>
                        <h3 className="font-semibold mb-1">{challenge.name}</h3>
                        <p className="text-sm text-muted-foreground leading-relaxed">{challenge.description}</p>
                      </div>
                      {challenge.joined && (
                        <Badge variant="secondary" className="bg-primary/20 text-primary flex-shrink-0">
                          Joined
                        </Badge>
                      )}
                    </div>

                    <div className="flex items-center gap-4 text-xs text-muted-foreground mb-3">
                      <div className="flex items-center gap-1">
                        <Users className="h-3 w-3" />
                        <span>{challenge.participants} participants</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        <span>{challenge.timeLeft}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Trophy className="h-3 w-3 text-accent" />
                        <span className="text-accent font-medium">{challenge.reward} pts</span>
                      </div>
                    </div>

                    {challenge.joined && (
                      <div className="space-y-2">
                        <div className="flex justify-between text-xs">
                          <span className="text-muted-foreground">Progress</span>
                          <div className="flex items-center gap-2">
                            <Button
                              size="sm"
                              variant="ghost"
                              className="h-6 w-6 p-0"
                              onClick={() => handleUpdateProgress(challenge.id, challenge.progress, -1)}
                              disabled={updatingId === challenge.id || challenge.progress <= 0}
                            >
                              <Minus className="h-3 w-3" />
                            </Button>
                            <span className="font-medium min-w-[60px] text-center">
                              {challenge.progress} / {challenge.target} {challenge.unit}
                            </span>
                            <Button
                              size="sm"
                              variant="ghost"
                              className="h-6 w-6 p-0"
                              onClick={() => handleUpdateProgress(challenge.id, challenge.progress, 1)}
                              disabled={updatingId === challenge.id || challenge.progress >= challenge.target}
                            >
                              <Plus className="h-3 w-3" />
                            </Button>
                          </div>
                        </div>
                        <div className="h-2 bg-muted rounded-full overflow-hidden">
                          <div
                            className="h-full bg-gradient-to-r from-primary to-accent transition-all"
                            style={{ width: `${Math.min((challenge.progress / challenge.target) * 100, 100)}%` }}
                          />
                        </div>
                      </div>
                    )}

                    {!challenge.joined && (
                      <Button
                        size="sm"
                        className="w-full mt-2 bg-primary hover:bg-primary/90 text-primary-foreground"
                        onClick={() => handleJoinChallenge(challenge.id)}
                        disabled={joiningId === challenge.id}
                      >
                        {joiningId === challenge.id ? "Joining..." : "Join Challenge"}
                      </Button>
                    )}
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </Card>
  )
}
