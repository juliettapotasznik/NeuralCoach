"use client"

import { useEffect, useState } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { UserPlus, Sparkles } from "lucide-react"
import { apiClient, SuggestedUser } from "@/lib/api"

export function UserProfilesCard() {
  const [suggestedUsers, setSuggestedUsers] = useState<SuggestedUser[]>([])
  const [loading, setLoading] = useState(true)
  const [addingId, setAddingId] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)  

  useEffect(() => {
    loadUsers()
  }, [])

  const loadUsers = async () => {
  try {
    setLoading(true)
    setError(null)
    const data = await apiClient.getSuggestedUsers(5)
    console.log("suggestedUsers from API:", data)   
    setSuggestedUsers(data)
  } catch (err) {
    console.error("Failed to fetch suggested users:", err)
    setError(err instanceof Error ? err.message : "Failed to load suggested users")
  } finally {
    setLoading(false)
  }
}

const handleAddFriend = async (userId: number) => {
  try {
      setAddingId(userId)
      await apiClient.addFriend(userId)
      await loadUsers()
    } catch (err) {
      console.error("Failed to add friend:", err)
      alert(err instanceof Error ? err.message : "Failed to add friend")
    } finally {
      setAddingId(null)
    }
  }

  return (
    <Card className="p-6 glass-card">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center">
          <Sparkles className="h-5 w-5 text-accent" />
        </div>
        <div>
          <h2 className="text-xl font-semibold">Suggested</h2>
          <p className="text-sm text-muted-foreground">People to connect with</p>
        </div>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-destructive/10 text-destructive rounded-lg text-sm">
          {error}
        </div>
      )}

      {loading ? (
        <div className="text-center py-8 text-muted-foreground">Loading suggestions...</div>
      ) : suggestedUsers.length === 0 ? (
        <div className="text-center py-8 text-muted-foreground">
          No suggestions available
        </div>
      ) : (
        <div className="space-y-4">
          {suggestedUsers.map((user) => (
            <div
              key={user.id}
              className="p-4 rounded-lg border border-border/50 hover:border-primary/30 transition-all"
            >
              <div className="flex items-start gap-3 mb-3">
                <Avatar className="h-12 w-12">
                  <AvatarImage src={`/generic-placeholder-icon.png?height=48&width=48`} />
                  <AvatarFallback className="bg-primary/10 text-primary">{user.avatar}</AvatarFallback>
                </Avatar>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-semibold text-sm">{user.name}</span>
                    <Badge variant="secondary" className="text-xs bg-accent/20 text-accent">
                      Lv {user.level}
                    </Badge>
                  </div>
                  <p className="text-xs text-muted-foreground leading-relaxed mb-2">
                    {user.bio || "Fitness enthusiast"}
                  </p>
                  <p className="text-xs text-muted-foreground">{user.mutualFriends} mutual friends</p>
                </div>
              </div>

              <Button
                size="sm"
                className="w-full gap-2 bg-primary hover:bg-primary/90 text-primary-foreground"
                disabled={addingId === user.id}
                onClick={() => handleAddFriend(user.id)}
              >
                <UserPlus className="h-4 w-4" />
                {addingId === user.id ? "Sending..." : "Connect"}
              </Button>
            </div>
          ))}
        </div>
      )}
    </Card>
  )
}
