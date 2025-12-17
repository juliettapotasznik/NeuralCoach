"use client"

import { useEffect, useState, useRef } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Send, X } from "lucide-react"
import { apiClient, Message } from "@/lib/api"
import { format } from "date-fns"

interface ChatDialogProps {
  open: boolean
  onClose: () => void
  friendId: number
  friendName: string
  friendAvatar: string
  onMessagesRead?: () => void
}

export function ChatDialog({ open, onClose, friendId, friendName, friendAvatar, onMessagesRead }: ChatDialogProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [newMessage, setNewMessage] = useState("")
  const [sending, setSending] = useState(false)
  const [loading, setLoading] = useState(true)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const [currentUserId, setCurrentUserId] = useState<number | null>(null)

  useEffect(() => {
    if (open && friendId) {
      loadMessages()
      loadCurrentUser()
      const interval = setInterval(loadMessages, 5000) // Poll every 5 seconds
      return () => clearInterval(interval)
    }
  }, [open, friendId])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const loadCurrentUser = async () => {
    try {
      const user = await apiClient.getCurrentUser()
      setCurrentUserId(user.id)
    } catch (err) {
      console.error("Failed to load current user:", err)
    }
  }

  const loadMessages = async () => {
    try {
      setLoading(true)
      const data = await apiClient.getConversation(friendId)
      setMessages(data)
      // Notify parent that messages were read (backend marks them as read automatically)
      if (onMessagesRead) {
        onMessagesRead()
      }
    } catch (err) {
      console.error("Failed to load messages:", err)
    } finally {
      setLoading(false)
    }
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  const handleSend = async () => {
    if (!newMessage.trim() || sending) return

    try {
      setSending(true)
      await apiClient.sendMessage(friendId, newMessage.trim())
      setNewMessage("")
      await loadMessages()
    } catch (err) {
      console.error("Failed to send message:", err)
      alert(err instanceof Error ? err.message : "Failed to send message")
    } finally {
      setSending(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl h-[600px] flex flex-col p-0">
        {/* Header */}
        <DialogHeader className="px-6 py-4 border-b">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Avatar className="h-10 w-10">
                <AvatarFallback className="bg-primary/10 text-primary">{friendAvatar}</AvatarFallback>
              </Avatar>
              <DialogTitle>{friendName}</DialogTitle>
            </div>
            <Button variant="ghost" size="icon" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>
        </DialogHeader>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
          {loading && messages.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">Loading messages...</div>
          ) : messages.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No messages yet. Start the conversation!
            </div>
          ) : (
            messages.map((message) => {
              const isOwnMessage = currentUserId === message.sender_id
              const senderInitials = isOwnMessage
                ? "ME"
                : (message.sender_name || friendName).substring(0, 2).toUpperCase()

              return (
                <div
                  key={message.id}
                  className={`flex ${isOwnMessage ? "justify-end" : "justify-start"}`}
                >
                  <div className={`flex gap-2 max-w-[70%] ${isOwnMessage ? "flex-row-reverse" : ""}`}>
                    <Avatar className="h-8 w-8 flex-shrink-0">
                      <AvatarFallback className="bg-primary/10 text-primary text-xs">
                        {senderInitials}
                      </AvatarFallback>
                    </Avatar>
                    <div className={`flex flex-col ${isOwnMessage ? "items-end" : ""}`}>
                      <div
                        className={`px-4 py-2 rounded-lg ${
                          isOwnMessage
                            ? "bg-primary text-primary-foreground"
                            : "bg-muted"
                        }`}
                      >
                        <p className="text-sm whitespace-pre-wrap break-words">{message.content}</p>
                      </div>
                      <span className="text-xs text-muted-foreground mt-1">
                        {format(new Date(message.created_at), "HH:mm")}
                      </span>
                    </div>
                  </div>
                </div>
              )
            })
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="px-6 py-4 border-t">
          <div className="flex gap-2">
            <Input
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type a message..."
              disabled={sending}
              className="flex-1"
            />
            <Button onClick={handleSend} disabled={sending || !newMessage.trim()} size="icon">
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
