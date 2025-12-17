import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Clock, Eye, Heart, Sparkles } from "lucide-react"

const articles = [
  {
    id: 1,
    title: "The Science of Progressive Overload: Building Strength Systematically",
    excerpt:
      "Understanding how to progressively increase training stimulus is key to long-term gains. Learn the principles that drive muscle growth and strength development.",
    author: "Dr. Sarah Chen",
    authorAvatar: "SC",
    category: "Training",
    readTime: "8 min read",
    views: 2840,
    likes: 342,
    image: "/gym-weights-training.jpg",
  },
  {
    id: 2,
    title: "Nutrition Timing: Does It Really Matter for Muscle Growth?",
    excerpt:
      "Exploring the latest research on meal timing, protein distribution, and the anabolic window. Separate fact from fiction in nutrition science.",
    author: "Mike Rodriguez",
    authorAvatar: "MR",
    category: "Nutrition",
    readTime: "6 min read",
    views: 1920,
    likes: 287,
    image: "/healthy-meal-prep-nutrition.jpg",
  },
]

export function FeaturedArticles() {
  return (
    <Card className="p-6 glass-card">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center">
          <Sparkles className="h-5 w-5 text-accent" />
        </div>
        <div>
          <h2 className="text-xl font-semibold">Featured Articles</h2>
          <p className="text-sm text-muted-foreground">Top community content</p>
        </div>
      </div>

      <div className="space-y-6">
        {articles.map((article) => (
          <div
            key={article.id}
            className="group cursor-pointer rounded-lg border border-border/50 overflow-hidden hover:border-primary/30 transition-all"
          >
            <div className="aspect-[2/1] bg-muted overflow-hidden">
              <img
                src={article.image || "/placeholder.svg"}
                alt={article.title}
                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
              />
            </div>

            <div className="p-5">
              <div className="flex items-center gap-2 mb-3">
                <Badge variant="secondary" className="bg-primary/10 text-primary">
                  {article.category}
                </Badge>
                <div className="flex items-center gap-1 text-xs text-muted-foreground">
                  <Clock className="h-3 w-3" />
                  <span>{article.readTime}</span>
                </div>
              </div>

              <h3 className="text-lg font-semibold mb-2 group-hover:text-primary transition-colors leading-snug">
                {article.title}
              </h3>

              <p className="text-sm text-muted-foreground leading-relaxed mb-4">{article.excerpt}</p>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Avatar className="h-8 w-8">
                    <AvatarImage src="/placeholder.svg?height=32&width=32" />
                    <AvatarFallback className="bg-primary/10 text-primary text-xs">
                      {article.authorAvatar}
                    </AvatarFallback>
                  </Avatar>
                  <span className="text-sm font-medium">{article.author}</span>
                </div>

                <div className="flex items-center gap-4 text-sm text-muted-foreground">
                  <div className="flex items-center gap-1">
                    <Eye className="h-4 w-4" />
                    <span>{article.views.toLocaleString()}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Heart className="h-4 w-4" />
                    <span>{article.likes}</span>
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
