import { Navigation } from "@/components/navigation"
import { LeaderboardCard } from "@/components/community/leaderboard-card"
import { ChallengesCard } from "@/components/community/challenges-card"
import { FriendsCard } from "@/components/community/friends-card"
import { UserProfilesCard } from "@/components/community/user-profiles-card"
import { Users } from "lucide-react"

export default function CommunityPage() {
  return (
    <div className="min-h-screen">
      <Navigation />

      <div className="container mx-auto px-4 py-12">
        {/* Header */}
        <div className="text-center mb-12 space-y-4">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-card border border-primary/20">
            <Users className="h-4 w-4 text-primary" />
            <span className="text-sm font-medium">Community Hub</span>
          </div>

          <h1 className="text-4xl md:text-5xl font-bold text-balance">
            Connect & Compete with{" "}
            <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              Fitness Enthusiasts
            </span>
          </h1>

          <p className="text-muted-foreground text-lg max-w-2xl mx-auto text-pretty leading-relaxed">
            Join challenges, make friends, and earn rewards as you progress on your fitness journey
          </p>
        </div>

        {/* Community Grid */}
        <div className="grid gap-6 lg:grid-cols-3">
          {/* Left Column - Leaderboard & Challenges */}
          <div className="lg:col-span-2 space-y-6">
            <LeaderboardCard />
            <ChallengesCard />
          </div>

          {/* Right Column - Friends & Profiles */}
          <div className="space-y-6">
            <FriendsCard />
            <UserProfilesCard />
          </div>
        </div>
      </div>
    </div>
  )
}
