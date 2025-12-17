"use client"

import { useEffect, useState } from "react"
import { Card } from "@/components/ui/card"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Trophy, Medal, Award, TrendingUp } from "lucide-react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { apiClient, LeaderboardUser } from "@/lib/api"

const getRankIcon = (rank: number) => {
  if (rank === 1) return <Trophy className="h-5 w-5 text-accent" />
  if (rank === 2) return <Medal className="h-5 w-5 text-gray-400" />
  if (rank === 3) return <Award className="h-5 w-5 text-orange-400" />
  return <span className="text-sm font-semibold text-muted-foreground">{rank}</span>
}

function LeaderboardList({ data, currentUsername }: { data: LeaderboardUser[]; currentUsername?: string }) {
  return (
    <div className="space-y-2">
      {data.length === 0 ? (
        <div className="text-center py-8 text-muted-foreground">
          No leaderboard data available
        </div>
      ) : (
        data.map((user) => (
          <div
            key={user.rank}
            className={`flex items-center gap-4 p-4 rounded-lg transition-all ${
              user.rank <= 3
                ? "bg-gradient-to-r from-primary/5 to-accent/5 border border-primary/20"
                : "bg-muted/30 hover:bg-muted/50"
            }`}
          >
            <div className="w-8 flex items-center justify-center">{getRankIcon(user.rank)}</div>

            <Avatar className="h-10 w-10">
              <AvatarImage src={`/generic-placeholder-graphic.png?height=40&width=40`} />
              <AvatarFallback className="bg-primary/10 text-primary text-sm">{user.avatar}</AvatarFallback>
            </Avatar>

            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <span className="font-semibold text-sm">{user.name}</span>
                {currentUsername && user.name === currentUsername && (
                  <Badge variant="secondary" className="text-xs bg-primary/20 text-primary">
                    You
                  </Badge>
                )}
              </div>
              <p className="text-xs text-muted-foreground">{user.workouts} workouts completed</p>
            </div>

            <div className="text-right">
              <div className="font-bold text-primary">{user.points.toLocaleString()}</div>
              <div className="text-xs text-muted-foreground">points</div>
            </div>

            {user.trend === "up" && <TrendingUp className="h-4 w-4 text-green-500" />}
          </div>
        ))
      )}
    </div>
  )
}

export function LeaderboardCard() {
  const [weeklyLeaderboard, setWeeklyLeaderboard] = useState<LeaderboardUser[]>([])
  const [monthlyLeaderboard, setMonthlyLeaderboard] = useState<LeaderboardUser[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [currentUsername, setCurrentUsername] = useState<string>()

  useEffect(() => {
    const fetchLeaderboards = async () => {
      try {
        setLoading(true)
        setError(null)

        // Fetch current user to highlight them in the leaderboard
        try {
          const user = await apiClient.getCurrentUser()
          setCurrentUsername(user.username)
        } catch (err) {
          // User not logged in, that's okay
          console.log("User not logged in")
        }

        // Fetch both leaderboards
        const [weekly, monthly] = await Promise.all([
          apiClient.getWeeklyLeaderboard(8),
          apiClient.getMonthlyLeaderboard(5),
        ])

        setWeeklyLeaderboard(weekly)
        setMonthlyLeaderboard(monthly)
      } catch (err) {
        console.error("Failed to fetch leaderboards:", err)
        setError(err instanceof Error ? err.message : "Failed to load leaderboards")
      } finally {
        setLoading(false)
      }
    }

    fetchLeaderboards()
  }, [])

  return (
    <Card className="p-6 glass-card">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center">
          <Trophy className="h-5 w-5 text-accent" />
        </div>
        <div>
          <h2 className="text-xl font-semibold">Leaderboard</h2>
          <p className="text-sm text-muted-foreground">Top performers</p>
        </div>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-destructive/10 text-destructive rounded-lg text-sm">
          {error}
        </div>
      )}

      <Tabs defaultValue="weekly" className="w-full">
        <TabsList className="grid w-full grid-cols-2 glass-card mb-6">
          <TabsTrigger value="weekly">This Week</TabsTrigger>
          <TabsTrigger value="monthly">This Month</TabsTrigger>
        </TabsList>

        <TabsContent value="weekly">
          {loading ? (
            <div className="text-center py-8 text-muted-foreground">Loading...</div>
          ) : (
            <LeaderboardList data={weeklyLeaderboard} currentUsername={currentUsername} />
          )}
        </TabsContent>

        <TabsContent value="monthly">
          {loading ? (
            <div className="text-center py-8 text-muted-foreground">Loading...</div>
          ) : (
            <LeaderboardList data={monthlyLeaderboard} currentUsername={currentUsername} />
          )}
        </TabsContent>
      </Tabs>
    </Card>
  )
}
