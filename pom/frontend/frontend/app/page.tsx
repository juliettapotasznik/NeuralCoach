"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Navigation } from "@/components/navigation"
import { Dumbbell, Brain, Users, Trophy, Sparkles, ArrowRight } from "lucide-react"
import { apiClient } from "@/lib/api"

export default function HomePage() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [username, setUsername] = useState("")
  const router = useRouter()

  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    const token = localStorage.getItem("access_token")
    if (token) {
      try {
        const user = await apiClient.getCurrentUser()
        setIsAuthenticated(true)
        setUsername(user.username)
      } catch {
        setIsAuthenticated(false)
      }
    }
  }

  return (
    <div className="min-h-screen">
      <Navigation />

      {/* Hero Section */}
      <section className="relative overflow-hidden">
        {/* Background Effects */}
        <div className="absolute inset-0 -z-10">
          <div className="absolute top-20 left-10 w-72 h-72 bg-primary/20 rounded-full blur-3xl animate-pulse" />
          <div className="absolute bottom-20 right-10 w-96 h-96 bg-accent/20 rounded-full blur-3xl animate-pulse delay-1000" />
        </div>

        <div className="container mx-auto px-4 py-20 md:py-32">
          <div className="max-w-4xl mx-auto text-center space-y-8">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-card border border-primary/20">
              <Sparkles className="h-4 w-4 text-primary" />
              <span className="text-sm font-medium text-foreground">AI-Powered Fitness Coaching</span>
            </div>

            <h1 className="text-5xl md:text-7xl font-bold leading-tight text-balance">
              {isAuthenticated ? (
                <>
                  Welcome back,{" "}
                  <span className="bg-gradient-to-r from-primary via-accent to-primary bg-clip-text text-transparent animate-gradient">
                    {username}
                  </span>
                  !
                </>
              ) : (
                <>
                  Transform Your Fitness Journey with{" "}
                  <span className="bg-gradient-to-r from-primary via-accent to-primary bg-clip-text text-transparent animate-gradient">
                    AI Intelligence
                  </span>
                </>
              )}
            </h1>

            <p className="text-xl text-muted-foreground max-w-2xl mx-auto text-pretty leading-relaxed">
              {isAuthenticated
                ? "Continue your fitness journey with AI-powered training and nutrition plans."
                : "Get personalized training plans, AI-powered form analysis, custom meal plans, and join a thriving community of fitness enthusiasts."}
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center pt-4">
              {!isAuthenticated && (
                <Link href="/auth">
                  <Button
                    size="lg"
                    className="bg-primary hover:bg-primary/90 text-primary-foreground shadow-lg hover:shadow-primary/50 transition-all group"
                  >
                    Get Started Free
                    <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
                  </Button>
                </Link>
              )}
              <Link href="/dashboard">
                <Button size="lg" variant={isAuthenticated ? "default" : "outline"} className={isAuthenticated ? "bg-primary hover:bg-primary/90" : "border-primary/20 hover:bg-primary/5 bg-transparent"}>
                  {isAuthenticated ? "Go to Dashboard" : "View Dashboard"}
                  {isAuthenticated && <ArrowRight className="ml-2 h-4 w-4" />}
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="container mx-auto px-4 py-20">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">Everything You Need to Succeed</h2>
          <p className="text-muted-foreground text-lg">Comprehensive tools powered by artificial intelligence</p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card className="p-6 glass-card hover:shadow-lg hover:shadow-primary/10 transition-all group cursor-pointer">
            <div className="mb-4 relative">
              <div className="absolute inset-0 bg-primary/20 blur-xl rounded-full opacity-0 group-hover:opacity-100 transition-opacity" />
              <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center relative">
                <Brain className="h-6 w-6 text-primary" />
              </div>
            </div>
            <h3 className="text-xl font-semibold mb-2">AI Training Assistant</h3>
            <p className="text-muted-foreground text-sm leading-relaxed">
              Upload videos for form analysis and get personalized workout plans
            </p>
          </Card>

          <Card className="p-6 glass-card hover:shadow-lg hover:shadow-primary/10 transition-all group cursor-pointer">
            <div className="mb-4 relative">
              <div className="absolute inset-0 bg-accent/20 blur-xl rounded-full opacity-0 group-hover:opacity-100 transition-opacity" />
              <div className="w-12 h-12 rounded-xl bg-accent/10 flex items-center justify-center relative">
                <Dumbbell className="h-6 w-6 text-accent" />
              </div>
            </div>
            <h3 className="text-xl font-semibold mb-2">Personal Dashboard</h3>
            <p className="text-muted-foreground text-sm leading-relaxed">
              Track progress, achievements, and body metrics in one place
            </p>
          </Card>

          <Card className="p-6 glass-card hover:shadow-lg hover:shadow-primary/10 transition-all group cursor-pointer">
            <div className="mb-4 relative">
              <div className="absolute inset-0 bg-primary/20 blur-xl rounded-full opacity-0 group-hover:opacity-100 transition-opacity" />
              <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center relative">
                <Users className="h-6 w-6 text-primary" />
              </div>
            </div>
            <h3 className="text-xl font-semibold mb-2">Community & Challenges</h3>
            <p className="text-muted-foreground text-sm leading-relaxed">
              Connect with others, join challenges, and earn rewards
            </p>
          </Card>

          <Card className="p-6 glass-card hover:shadow-lg hover:shadow-primary/10 transition-all group cursor-pointer">
            <div className="mb-4 relative">
              <div className="absolute inset-0 bg-accent/20 blur-xl rounded-full opacity-0 group-hover:opacity-100 transition-opacity" />
              <div className="w-12 h-12 rounded-xl bg-accent/10 flex items-center justify-center relative">
                <Trophy className="h-6 w-6 text-accent" />
              </div>
            </div>
            <h3 className="text-xl font-semibold mb-2">Smart Nutrition</h3>
            <p className="text-muted-foreground text-sm leading-relaxed">
              AI-generated meal plans tailored to your goals and preferences
            </p>
          </Card>
        </div>
      </section>

      {/* CTA Section - tylko dla niezalogowanych */}
      {!isAuthenticated && (
        <section className="container mx-auto px-4 py-20">
          <Card className="relative overflow-hidden glass-card neon-border">
            <div className="absolute inset-0 bg-gradient-to-r from-primary/10 via-accent/10 to-primary/10" />
            <div className="relative p-12 text-center">
              <h2 className="text-3xl md:text-4xl font-bold mb-4">Ready to Start Your Journey?</h2>
              <p className="text-muted-foreground text-lg mb-8 max-w-2xl mx-auto">
                Join thousands of users transforming their fitness with AI-powered coaching
              </p>
              <Link href="/auth">
                <Button
                  size="lg"
                  className="bg-primary hover:bg-primary/90 text-primary-foreground shadow-lg hover:shadow-primary/50"
                >
                  Get Started Free
                </Button>
              </Link>
            </div>
          </Card>
        </section>
      )}
    </div>
  )
}
