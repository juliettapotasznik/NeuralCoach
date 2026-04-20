import { Navigation } from "@/components/navigation"
import { FeaturedArticles } from "@/components/forum/featured-articles"
import { ForumCategories } from "@/components/forum/forum-categories"
import { RecentDiscussions } from "@/components/forum/recent-discussions"
import { TopContributors } from "@/components/forum/top-contributors"
import { Button } from "@/components/ui/button"
import { BookOpen, Plus } from "lucide-react"

export default function ForumPage() {
  return (
    <div className="min-h-screen">
      <Navigation />

      <div className="container mx-auto px-4 py-12">
        {/* Header */}
        <div className="text-center mb-12 space-y-4">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-card border border-primary/20">
            <BookOpen className="h-4 w-4 text-primary" />
            <span className="text-sm font-medium">Knowledge Hub</span>
          </div>

          <h1 className="text-4xl md:text-5xl font-bold text-balance">
            Learn from the{" "}
            <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">Community</span>
          </h1>

          <p className="text-muted-foreground text-lg max-w-2xl mx-auto text-pretty leading-relaxed">
            Discover expert articles, join discussions, and share your fitness knowledge
          </p>

          <Button size="lg" className="gap-2 bg-primary hover:bg-primary/90 text-primary-foreground">
            <Plus className="h-4 w-4" />
            Create Post
          </Button>
        </div>

        {/* Main Content */}
        <div className="grid gap-6 lg:grid-cols-3">
          {/* Left Column - Articles & Discussions */}
          <div className="lg:col-span-2 space-y-6">
            <FeaturedArticles />
            <ForumCategories />
            <RecentDiscussions />
          </div>

          {/* Right Column - Contributors */}
          <div>
            <TopContributors />
          </div>
        </div>
      </div>
    </div>
  )
}
