import { Card } from "@/components/ui/card"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { MessageSquare, TrendingUp, Clock } from "lucide-react"

const discussions = [
  {
    id: 1,
    title: "Best exercises for building a strong posterior chain?",
    author: "James Lee",
    authorAvatar: "JL",
    category: "Training",
    replies: 24,
    views: 342,
    lastActivity: "2 hours ago",
    trending: true,
  },
  {
    id: 2,
    title: "Struggling with sleep quality - any tips?",
    author: "Emma Wilson",
    authorAvatar: "EW",
    category: "Recovery",
    replies: 18,
    views: 256,
    lastActivity: "4 hours ago",
    trending: false,
  },
  {
    id: 3,
    title: "Macro split for cutting while maintaining strength",
    author: "David Kim",
    authorAvatar: "DK",
    category: "Nutrition",
    replies: 31,
    views: 489,
    lastActivity: "5 hours ago",
    trending: true,
  },
  {
    id: 4,
    title: "How to stay motivated during a plateau?",
    author: "Lisa Park",
    authorAvatar: "LP",
    category: "Mindset",
    replies: 15,
    views: 198,
    lastActivity: "8 hours ago",
    trending: false,
  },
  {
    id: 5,
    title: "Form check: My squat depth seems off",
    author: "Rachel Green",
    authorAvatar: "RG",
    category: "Training",
    replies: 12,
    views: 167,
    lastActivity: "1 day ago",
    trending: false,
  },
]

export function RecentDiscussions() {
  return (
    <Card className="p-6 glass-card">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
          <MessageSquare className="h-5 w-5 text-primary" />
        </div>
        <div>
          <h2 className="text-xl font-semibold">Recent Discussions</h2>
          <p className="text-sm text-muted-foreground">Active conversations</p>
        </div>
      </div>

      <div className="space-y-3">
        {discussions.map((discussion) => (
          <div
            key={discussion.id}
            className="p-4 rounded-lg border border-border/50 hover:border-primary/30 transition-all cursor-pointer group"
          >
            <div className="flex items-start gap-3">
              <Avatar className="h-10 w-10 flex-shrink-0">
                <AvatarImage src="/placeholder.svg?height=40&width=40" />
                <AvatarFallback className="bg-primary/10 text-primary text-sm">
                  {discussion.authorAvatar}
                </AvatarFallback>
              </Avatar>

              <div className="flex-1 min-w-0">
                <div className="flex items-start gap-2 mb-2">
                  <h3 className="font-semibold text-sm group-hover:text-primary transition-colors leading-snug flex-1">
                    {discussion.title}
                  </h3>
                  {discussion.trending && <TrendingUp className="h-4 w-4 text-accent flex-shrink-0 mt-0.5" />}
                </div>

                <div className="flex items-center gap-3 text-xs text-muted-foreground mb-2">
                  <span className="font-medium">{discussion.author}</span>
                  <Badge variant="secondary" className="text-xs">
                    {discussion.category}
                  </Badge>
                </div>

                <div className="flex items-center gap-4 text-xs text-muted-foreground">
                  <div className="flex items-center gap-1">
                    <MessageSquare className="h-3 w-3" />
                    <span>{discussion.replies} replies</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    <span>{discussion.lastActivity}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </Card>
  )
}
