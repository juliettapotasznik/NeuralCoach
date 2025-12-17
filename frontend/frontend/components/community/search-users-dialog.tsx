"use client"

import { useState } from "react"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Search, UserPlus, Check, Clock } from "lucide-react"
import { apiClient, SearchedUser } from "@/lib/api"

interface SearchUsersDialogProps {
  open: boolean
  onClose: () => void
  onFriendAdded: () => void
}

export function SearchUsersDialog({ open, onClose, onFriendAdded }: SearchUsersDialogProps) {
  const [searchQuery, setSearchQuery] = useState("")
  const [searchResults, setSearchResults] = useState<SearchedUser[]>([])
  const [searching, setSearching] = useState(false)
  const [addingId, setAddingId] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleSearch = async () => {
    if (searchQuery.length < 2) {
      setError("Search query must be at least 2 characters")
      return
    }

    setSearching(true)
    setError(null)

    try {
      const results = await apiClient.searchUsers(searchQuery)
      setSearchResults(results)
    } catch (err) {
      console.error("Failed to search users:", err)
      setError(err instanceof Error ? err.message : "Failed to search users")
    } finally {
      setSearching(false)
    }
  }

  const handleAddFriend = async (userId: number) => {
    setAddingId(userId)
    try {
      await apiClient.addFriend(userId)
      // Update the search results to reflect the pending request
      setSearchResults(searchResults.map(user =>
        user.id === userId ? { ...user, has_pending_request: true } : user
      ))
      onFriendAdded()
    } catch (err) {
      console.error("Failed to add friend:", err)
      setError(err instanceof Error ? err.message : "Failed to add friend")
    } finally {
      setAddingId(null)
    }
  }

  const handleClose = () => {
    setSearchQuery("")
    setSearchResults([])
    setError(null)
    onClose()
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      handleSearch()
    }
  }

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Search Users</DialogTitle>
          <DialogDescription>Find and add friends by username</DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Search Input */}
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by username..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={handleKeyPress}
                className="pl-9"
              />
            </div>
            <Button onClick={handleSearch} disabled={searching || searchQuery.length < 2}>
              {searching ? "Searching..." : "Search"}
            </Button>
          </div>

          {error && (
            <div className="p-3 bg-destructive/10 text-destructive rounded-lg text-sm">
              {error}
            </div>
          )}

          {/* Search Results */}
          <div className="space-y-2 max-h-[400px] overflow-y-auto">
            {searchResults.length === 0 && !searching && searchQuery && (
              <div className="text-center py-8 text-muted-foreground">
                No users found matching "{searchQuery}"
              </div>
            )}

            {searchResults.map((user) => (
              <div
                key={user.id}
                className="flex items-center gap-3 p-3 rounded-lg border border-border/50 hover:border-primary/30 transition-colors"
              >
                <Avatar className="h-10 w-10">
                  <AvatarFallback className="bg-primary/10 text-primary text-sm">
                    {user.avatar}
                  </AvatarFallback>
                </Avatar>

                <div className="flex-1">
                  <div className="font-semibold text-sm">{user.username}</div>
                  <div className="text-xs text-muted-foreground">Level {user.level}</div>
                </div>

                {user.is_friend ? (
                  <Button size="sm" variant="outline" disabled className="gap-2">
                    <Check className="h-4 w-4" />
                    Friends
                  </Button>
                ) : user.has_pending_request ? (
                  <Button size="sm" variant="outline" disabled className="gap-2">
                    <Clock className="h-4 w-4" />
                    Pending
                  </Button>
                ) : (
                  <Button
                    size="sm"
                    variant="outline"
                    className="gap-2"
                    onClick={() => handleAddFriend(user.id)}
                    disabled={addingId === user.id}
                  >
                    <UserPlus className="h-4 w-4" />
                    {addingId === user.id ? "Adding..." : "Add"}
                  </Button>
                )}
              </div>
            ))}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
