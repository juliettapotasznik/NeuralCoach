"use client"

import { useEffect, useState } from "react"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Trophy, Target, Flame, Award, Lock, Dumbbell, Users } from "lucide-react"
import { apiClient, Achievement } from "@/lib/api"
import { format } from "date-fns"

const iconMap: Record<string, any> = {
  Target,
  Flame,
  Trophy,
  Award,
  Dumbbell,
  Users
}

export function AchievementsCard() {
  const [achievements, setAchievements] = useState<Achievement[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadAchievements()
  }, [])

  const loadAchievements = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await apiClient.getAchievements()
      // Filter to show only NOT unlocked achievements (in progress)
      const inProgressAchievements = data.filter((a) => !a.unlocked)
      setAchievements(inProgressAchievements)
    } catch (err) {
      console.error("Failed to fetch achievements:", err)
      setError(err instanceof Error ? err.message : "Failed to load achievements")
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card className="p-6 glass-card h-full">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center">
            <Trophy className="h-5 w-5 text-accent" />
          </div>
          <div>
            <h2 className="text-xl font-semibold">Achievements</h2>
            <p className="text-sm text-muted-foreground">
              {loading ? "Loading..." : `${achievements.length} in progress`}
            </p>
          </div>
        </div>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-destructive/10 text-destructive rounded-lg text-sm">
          {error}
        </div>
      )}

      {loading ? (
        <div className="text-center py-8 text-muted-foreground">Loading achievements...</div>
      ) : achievements.length === 0 ? (
        <div className="text-center py-8 text-muted-foreground">
          No achievements available yet
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          {achievements.map((achievement) => {
            const Icon = iconMap[achievement.icon] || Trophy
            return (
              <div
                key={achievement.id}
                className={`p-4 rounded-lg border transition-all ${
                  achievement.unlocked
                    ? "bg-accent/5 border-accent/20 hover:border-accent/40"
                    : "bg-muted/30 border-border/50 opacity-60"
                }`}
              >
                <div className="flex items-start gap-3">
                  <div
                    className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${
                      achievement.unlocked ? "bg-accent/20" : "bg-muted"
                    }`}
                  >
                    {achievement.unlocked ? (
                      <Icon className="h-5 w-5 text-accent" />
                    ) : (
                      <Lock className="h-5 w-5 text-muted-foreground" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-sm mb-1">{achievement.name}</h3>
                    <p className="text-xs text-muted-foreground leading-relaxed mb-2">
                      {achievement.description}
                    </p>
                    {achievement.unlocked ? (
                      <Badge variant="secondary" className="text-xs bg-accent/20 text-accent-foreground">
                        {achievement.unlocked_at
                          ? format(new Date(achievement.unlocked_at), "MMM d, yyyy")
                          : "Unlocked"}
                      </Badge>
                    ) : (
                      <div className="space-y-1">
                        <div className="flex justify-between text-xs text-muted-foreground">
                          <span>Progress</span>
                          <span>
                            {achievement.progress}/{achievement.requirement}
                          </span>
                        </div>
                        <div className="h-1.5 bg-muted rounded-full overflow-hidden">
                          <div
                            className="h-full bg-primary transition-all"
                            style={{
                              width: `${Math.min((achievement.progress / achievement.requirement) * 100, 100)}%`
                            }}
                          />
                        </div>
                      </div>
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
