"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Dumbbell, LayoutDashboard, Users, BookOpen, UtensilsCrossed, Menu, X, Settings, LogOut, Library } from "lucide-react"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { apiClient } from "@/lib/api"

const navItems = [
  { name: "AI Training", href: "/training", icon: Dumbbell },
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { name: "Exercise Catalog", href: "/exercises", icon: Library },
  { name: "Community", href: "/community", icon: Users },
  { name: "Forum", href: "/forum", icon: BookOpen },
  { name: "Diet", href: "/diet", icon: UtensilsCrossed },
]

export function Navigation() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [username, setUsername] = useState<string>("")
  const [unreadCount, setUnreadCount] = useState(0)
  const router = useRouter()

  useEffect(() => {
    checkAuth()
  }, [])

  useEffect(() => {
    if (isAuthenticated) {
      loadUnreadCount()
      // Poll for unread messages every 30 seconds
      const interval = setInterval(loadUnreadCount, 30000)

      // Listen for custom event to refresh unread count
      const handleRefresh = () => loadUnreadCount()
      window.addEventListener('refreshUnreadCount', handleRefresh)

      return () => {
        clearInterval(interval)
        window.removeEventListener('refreshUnreadCount', handleRefresh)
      }
    }
  }, [isAuthenticated])

  const checkAuth = async () => {
    const token = localStorage.getItem("access_token")
    if (token) {
      setIsAuthenticated(true)
      try {
        const user = await apiClient.getCurrentUser()
        setUsername(user.username)
      } catch (err) {
        console.error("Failed to fetch user:", err)
        setIsAuthenticated(false)
        localStorage.removeItem("access_token")
      }
    }
  }

  const loadUnreadCount = async () => {
    try {
      const data = await apiClient.getUnreadCount()
      setUnreadCount(data.unread_count)
    } catch (err) {
      console.error("Failed to fetch unread count:", err)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem("access_token")
    setIsAuthenticated(false)
    setUsername("")
    router.push("/")
  }

  return (
    <nav className="sticky top-0 z-50 w-full border-b border-border/40 glass-card">
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2 group">
            <div className="relative">
              <div className="absolute inset-0 bg-primary/20 blur-xl rounded-full group-hover:bg-primary/30 transition-all" />
              <Dumbbell className="h-8 w-8 text-primary relative" />
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              NeuralCoach
            </span>
          </Link>

          {/* Desktop Navigation - tylko dla zalogowanych */}
          {isAuthenticated && (
            <div className="hidden md:flex items-center gap-1">
              {navItems.map((item) => (
                <Link key={item.name} href={item.href}>
                  <Button variant="ghost" className="gap-2 hover:bg-primary/10 hover:text-primary transition-all relative">
                    <item.icon className="h-4 w-4" />
                    {item.name}
                    {item.name === "Community" && unreadCount > 0 && (
                      <Badge className="absolute -top-1 -right-1 h-5 w-5 flex items-center justify-center p-0 bg-destructive text-destructive-foreground text-xs">
                        {unreadCount > 9 ? "9+" : unreadCount}
                      </Badge>
                    )}
                  </Button>
                </Link>
              ))}
            </div>
          )}

          {/* User Menu lub Get Started */}
          <div className="hidden md:flex md:items-center md:gap-2">
            {isAuthenticated ? (
              <>
                <Button
                  variant="ghost"
                  className="gap-2 hover:bg-primary/10"
                  onClick={() => router.push("/settings")}
                >
                  <Avatar className="h-8 w-8">
                    <AvatarFallback className="bg-primary/10 text-primary text-sm">
                      {username.substring(0, 2).toUpperCase()}
                    </AvatarFallback>
                  </Avatar>
                  <span>{username}</span>
                </Button>
                <Button variant="ghost" size="sm" onClick={handleLogout} className="gap-2 text-destructive">
                  <LogOut className="h-4 w-4" />
                  Logout
                </Button>
              </>
            ) : (
              <Link href="/auth">
                <Button className="bg-primary hover:bg-primary/90 text-primary-foreground shadow-lg hover:shadow-primary/50 transition-all">
                  Get Started
                </Button>
              </Link>
            )}
          </div>

          {/* Mobile Menu Button */}
          <Button variant="ghost" size="icon" className="md:hidden" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
            {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </Button>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden py-4 space-y-2 animate-in slide-in-from-top">
            {isAuthenticated && navItems.map((item) => (
              <Link key={item.name} href={item.href}>
                <Button
                  variant="ghost"
                  className="w-full justify-start gap-2 hover:bg-primary/10 hover:text-primary relative"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  <item.icon className="h-4 w-4" />
                  {item.name}
                  {item.name === "Community" && unreadCount > 0 && (
                    <Badge className="ml-auto h-5 w-5 flex items-center justify-center p-0 bg-destructive text-destructive-foreground text-xs">
                      {unreadCount > 9 ? "9+" : unreadCount}
                    </Badge>
                  )}
                </Button>
              </Link>
            ))}
            {isAuthenticated ? (
              <>
                <Button
                  variant="ghost"
                  className="w-full justify-start gap-2"
                  onClick={() => {
                    router.push("/settings")
                    setMobileMenuOpen(false)
                  }}
                >
                  <Settings className="h-4 w-4" />
                  Settings
                </Button>
                <Button
                  variant="ghost"
                  className="w-full justify-start gap-2 text-destructive"
                  onClick={() => {
                    handleLogout()
                    setMobileMenuOpen(false)
                  }}
                >
                  <LogOut className="h-4 w-4" />
                  Logout
                </Button>
              </>
            ) : (
              <Link href="/auth">
                <Button className="w-full bg-primary hover:bg-primary/90 text-primary-foreground mt-4">
                  Get Started
                </Button>
              </Link>
            )}
          </div>
        )}
      </div>
    </nav>
  )
}
