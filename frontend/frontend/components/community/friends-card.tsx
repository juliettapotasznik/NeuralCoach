"use client"

import { useEffect, useState } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { UserPlus, Users, MessageSquare } from "lucide-react"
import { apiClient, Friend, FriendRequest } from "@/lib/api"
import { ChatDialog } from "./chat-dialog"
import { SearchUsersDialog } from "./search-users-dialog"

export function FriendsCard() {
  const [friends, setFriends] = useState<Friend[]>([])
  const [requests, setRequests] = useState<FriendRequest[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [chatOpen, setChatOpen] = useState(false)
  const [searchOpen, setSearchOpen] = useState(false)
  const [selectedFriend, setSelectedFriend] = useState<{ id: number; name: string; avatar: string } | null>(null)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      setError(null)
      const [friendsData, requestsData] = await Promise.all([
        apiClient.getFriends(),
        apiClient.getFriendRequests()
      ])
      setFriends(friendsData)
      setRequests(requestsData)
    } catch (err) {
      console.error("Failed to fetch data:", err)
      setError(err instanceof Error ? err.message : "Failed to load data")
    } finally {
      setLoading(false)
    }
  }

  const handleAcceptRequest = async (requestId: number) => {
    try {
      await apiClient.acceptFriendRequest(requestId)
      await loadData()
    } catch (err) {
      console.error("Failed to accept request:", err)
      alert(err instanceof Error ? err.message : "Failed to accept request")
    }
  }

  const handleRejectRequest = async (requestId: number) => {
    try {
      await apiClient.rejectFriendRequest(requestId)
      await loadData()
    } catch (err) {
      console.error("Failed to reject request:", err)
      alert(err instanceof Error ? err.message : "Failed to reject request")
    }
  }

  const handleOpenChat = (friend: Friend) => {
    setSelectedFriend({ id: friend.id, name: friend.name, avatar: friend.avatar })
    setChatOpen(true)
  }

  const handleMessagesRead = () => {
    // Reload friends list to update unread counts
    loadData()
    // Notify navigation to refresh unread count
    window.dispatchEvent(new Event('refreshUnreadCount'))
  }

  return (
    <Card className="p-6 glass-card">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
            <Users className="h-5 w-5 text-primary" />
          </div>
          <div>
            <h2 className="text-xl font-semibold">Friends</h2>
            <p className="text-sm text-muted-foreground">{friends.length} connections</p>
          </div>
        </div>
        <Button size="sm" variant="outline" className="gap-2 bg-transparent" onClick={() => setSearchOpen(true)}>
          <UserPlus className="h-4 w-4" />
          Add
        </Button>
      </div>

      <SearchUsersDialog
        open={searchOpen}
        onClose={() => setSearchOpen(false)}
        onFriendAdded={loadData}
      />

      {error && (
        <div className="mb-4 p-3 bg-destructive/10 text-destructive rounded-lg text-sm">
          {error}
        </div>
      )}

      {loading ? (
        <div className="text-center py-8 text-muted-foreground">Loading...</div>
      ) : (
        <>
          {/* Friend Requests */}
          {requests.length > 0 && (
            <div className="mb-6">
              <h3 className="text-sm font-semibold mb-3">Friend Requests ({requests.length})</h3>
              <div className="space-y-2">
                {requests.map((request) => (
                  <div key={request.id} className="flex items-center gap-3 p-3 rounded-lg bg-muted/30">
                    <Avatar className="h-10 w-10">
                      <AvatarFallback className="bg-primary/10 text-primary text-sm">
                        {request.avatar}
                      </AvatarFallback>
                    </Avatar>
                    <div className="flex-1 min-w-0">
                      <div className="font-semibold text-sm">{request.username}</div>
                      <p className="text-xs text-muted-foreground">Wants to connect</p>
                    </div>
                    <div className="flex gap-2">
                      <Button size="sm" variant="default" onClick={() => handleAcceptRequest(request.id)}>
                        Accept
                      </Button>
                      <Button size="sm" variant="ghost" onClick={() => handleRejectRequest(request.id)}>
                        Decline
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Friends List */}
          {friends.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No friends yet. Start connecting!
            </div>
          ) : (
            <div className="space-y-3">
              {friends.map((friend) => (
                <div key={friend.id} className="flex items-center gap-3 p-3 rounded-lg hover:bg-muted/50 transition-colors">
                  <div className="relative">
                    <Avatar className="h-10 w-10">
                      <AvatarImage src={`/generic-placeholder-graphic.png?height=40&width=40`} />
                      <AvatarFallback className="bg-primary/10 text-primary text-sm">{friend.avatar}</AvatarFallback>
                    </Avatar>
                    {friend.online && (
                      <div className="absolute bottom-0 right-0 w-3 h-3 bg-green-500 rounded-full border-2 border-card" />
                    )}
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="font-semibold text-sm">{friend.name}</div>
                    <p className="text-xs text-muted-foreground truncate">{friend.status || "Active"}</p>
                  </div>

                  <Button
                    size="sm"
                    variant="ghost"
                    className="h-8 w-8 p-0 relative"
                    onClick={() => handleOpenChat(friend)}
                  >
                    <MessageSquare className="h-4 w-4" />
                    {friend.unread_count > 0 && (
                      <Badge className="absolute -top-1 -right-1 h-4 w-4 flex items-center justify-center p-0 bg-destructive text-destructive-foreground text-[10px]">
                        {friend.unread_count > 9 ? "9+" : friend.unread_count}
                      </Badge>
                    )}
                  </Button>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {selectedFriend && (
        <ChatDialog
          open={chatOpen}
          onClose={() => setChatOpen(false)}
          friendId={selectedFriend.id}
          friendName={selectedFriend.name}
          friendAvatar={selectedFriend.avatar}
          onMessagesRead={handleMessagesRead}
        />
      )}
    </Card>
  )
}
