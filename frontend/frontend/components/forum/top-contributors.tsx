import { Card } from "@/components/ui/card"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Award, TrendingUp } from "lucide-react"

const contributors = [
  {
    rank: 1,
    name: "Dr. Sarah Chen",
    avatar: "SC",
    badge: "Expert",
    badgeColor: "bg-accent/20 text-accent",
    posts: 156,
    likes: 3420,
    level: 42,
  },
  {
    rank: 2,
    name: "Mike Rodriguez",
    avatar: "MR",
    badge: "Veteran",
    badgeColor: "bg-primary/20 text-primary",
    posts: 134,
    likes: 2890,
    level: 38,
  },
  {
    rank: 3,
    name: "Emma Wilson",
    avatar: "EW",
    badge: "Contributor",
    badgeColor: "bg-chart-3/20 text-chart-3",
    posts: 98,
    likes: 2156,
    level: 32,
  },
  {
    rank: 4,
    name: "James Lee",
    avatar: "JL",
    badge: "Active",
    badgeColor: "bg-chart-4/20 text-chart-4",
    posts: 87,
    likes: 1843,
    level: 28,
  },
  {
    rank: 5,
    name: "Lisa Park",
    avatar: "LP",
    badge: "Rising Star",
    badgeColor: "bg-accent/20 text-accent",
    posts: 72,
    likes: 1567,
    level: 24,
  },
]

export function TopContributors() {
  return (
    <Card className="p-6 glass-card sticky top-24">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center">
          <Award className="h-5 w-5 text-accent" />
        </div>
        <div>
          <h2 className="text-xl font-semibold">Top Contributors</h2>
          <p className="text-sm text-muted-foreground">This month</p>
        </div>
      </div>

      <div className="space-y-4">
        {contributors.map((contributor) => (
          <div
            key={contributor.rank}
            className={`p-4 rounded-lg transition-all cursor-pointer ${
              contributor.rank <= 3
                ? "bg-gradient-to-r from-primary/5 to-accent/5 border border-primary/20"
                : "bg-muted/30 hover:bg-muted/50"
            }`}
          >
            <div className="flex items-start gap-3">
              <div className="relative">
                <Avatar className="h-12 w-12">
                  <AvatarImage src="/placeholder.svg?height=48&width=48" />
                  <AvatarFallback className="bg-primary/10 text-primary">{contributor.avatar}</AvatarFallback>
                </Avatar>
                <div className="absolute -top-1 -right-1 w-6 h-6 rounded-full bg-accent text-accent-foreground flex items-center justify-center text-xs font-bold">
                  {contributor.rank}
                </div>
              </div>

              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-semibold text-sm">{contributor.name}</span>
                  {contributor.rank === 1 && <TrendingUp className="h-3 w-3 text-accent" />}
                </div>

                <div className="flex items-center gap-2 mb-2">
                  <Badge variant="secondary" className={`text-xs ${contributor.badgeColor}`}>
                    {contributor.badge}
                  </Badge>
                  <span className="text-xs text-muted-foreground">Lv {contributor.level}</span>
                </div>

                <div className="flex items-center gap-3 text-xs text-muted-foreground">
                  <span>{contributor.posts} posts</span>
                  <span>{contributor.likes.toLocaleString()} likes</span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-6 p-4 rounded-lg bg-primary/5 border border-primary/20">
        <div className="flex items-start gap-3">
          <Award className="h-5 w-5 text-primary flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="font-semibold text-sm mb-1">Earn Badges</h4>
            <p className="text-xs text-muted-foreground leading-relaxed">
              Post helpful content, engage with the community, and unlock special badges and ranks!
            </p>
          </div>
        </div>
      </div>
    </Card>
  )
}
