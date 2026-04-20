import { Card } from "@/components/ui/card"
import { Dumbbell, Apple, Brain, Heart, MessageSquare } from "lucide-react"

const categories = [
  {
    name: "Training",
    icon: Dumbbell,
    topics: 342,
    posts: 2840,
    color: "text-primary",
    bgColor: "bg-primary/10",
  },
  {
    name: "Nutrition",
    icon: Apple,
    topics: 289,
    posts: 2156,
    color: "text-accent",
    bgColor: "bg-accent/10",
  },
  {
    name: "Recovery",
    icon: Heart,
    topics: 178,
    posts: 1432,
    color: "text-chart-3",
    bgColor: "bg-chart-3/10",
  },
  {
    name: "Mindset",
    icon: Brain,
    topics: 156,
    posts: 1089,
    color: "text-chart-4",
    bgColor: "bg-chart-4/10",
  },
]

export function ForumCategories() {
  return (
    <Card className="p-6 glass-card">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
          <MessageSquare className="h-5 w-5 text-primary" />
        </div>
        <div>
          <h2 className="text-xl font-semibold">Forum Categories</h2>
          <p className="text-sm text-muted-foreground">Browse by topic</p>
        </div>
      </div>

      <div className="grid sm:grid-cols-2 gap-4">
        {categories.map((category) => (
          <div
            key={category.name}
            className="p-5 rounded-lg border border-border/50 hover:border-primary/30 transition-all cursor-pointer group"
          >
            <div className="flex items-start gap-4">
              <div
                className={`w-12 h-12 rounded-lg ${category.bgColor} flex items-center justify-center flex-shrink-0`}
              >
                <category.icon className={`h-6 w-6 ${category.color}`} />
              </div>

              <div className="flex-1 min-w-0">
                <h3 className="font-semibold mb-2 group-hover:text-primary transition-colors">{category.name}</h3>
                <div className="flex items-center gap-4 text-xs text-muted-foreground">
                  <span>{category.topics} topics</span>
                  <span>{category.posts.toLocaleString()} posts</span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </Card>
  )
}
