"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { Navigation } from "@/components/navigation"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Settings, Lock, User, Upload, Trash2, CheckCircle, AlertCircle } from "lucide-react"
import { apiClient } from "@/lib/api"

export default function SettingsPage() {
  const [username, setUsername] = useState<string>("")
  const [email, setEmail] = useState<string>("")
  const [profilePicture, setProfilePicture] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  // Password change state
  const [currentPassword, setCurrentPassword] = useState("")
  const [newPassword, setNewPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [passwordError, setPasswordError] = useState<string | null>(null)
  const [passwordSuccess, setPasswordSuccess] = useState<string | null>(null)
  const [changingPassword, setChangingPassword] = useState(false)

  // Profile picture state
  const [uploadingPicture, setUploadingPicture] = useState(false)
  const [pictureError, setPictureError] = useState<string | null>(null)
  const [pictureSuccess, setPictureSuccess] = useState<string | null>(null)

  useEffect(() => {
    loadUser()
  }, [])

  const loadUser = async () => {
    try {
      const user = await apiClient.getCurrentUser()
      setUsername(user.username)
      setEmail(user.email)
      setProfilePicture(user.profile_picture)
    } catch (err) {
      console.error("Failed to load user:", err)
      router.push("/auth")
    } finally {
      setLoading(false)
    }
  }

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault()
    setPasswordError(null)
    setPasswordSuccess(null)

    if (newPassword !== confirmPassword) {
      setPasswordError("New passwords do not match")
      return
    }

    if (newPassword.length < 6) {
      setPasswordError("New password must be at least 6 characters")
      return
    }

    setChangingPassword(true)

    try {
      const result = await apiClient.changePassword(currentPassword, newPassword)
      setPasswordSuccess(result.message)
      setCurrentPassword("")
      setNewPassword("")
      setConfirmPassword("")
    } catch (err) {
      setPasswordError(err instanceof Error ? err.message : "Failed to change password")
    } finally {
      setChangingPassword(false)
    }
  }

  const handlePictureUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    // Validate file type
    const allowedTypes = ["image/jpeg", "image/jpg", "image/png"]
    if (!allowedTypes.includes(file.type)) {
      setPictureError("Only JPG, JPEG, and PNG files are allowed")
      return
    }

    // Validate file size (5MB)
    if (file.size > 5 * 1024 * 1024) {
      setPictureError("File size must be less than 5MB")
      return
    }

    setPictureError(null)
    setPictureSuccess(null)
    setUploadingPicture(true)

    try {
      const result = await apiClient.uploadProfilePicture(file)
      setProfilePicture(result.profile_picture)
      setPictureSuccess("Profile picture updated successfully")
    } catch (err) {
      setPictureError(err instanceof Error ? err.message : "Failed to upload picture")
    } finally {
      setUploadingPicture(false)
    }
  }

  const handlePictureDelete = async () => {
    setPictureError(null)
    setPictureSuccess(null)
    setUploadingPicture(true)

    try {
      await apiClient.deleteProfilePicture()
      setProfilePicture(null)
      setPictureSuccess("Profile picture deleted successfully")
    } catch (err) {
      setPictureError(err instanceof Error ? err.message : "Failed to delete picture")
    } finally {
      setUploadingPicture(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen">
        <Navigation />
        <div className="container mx-auto px-4 py-12">
          <div className="text-center py-8 text-muted-foreground">Loading settings...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen">
      <Navigation />

      <div className="container mx-auto px-4 py-12 max-w-4xl">
        {/* Header */}
        <div className="mb-8 space-y-4">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-card border border-primary/20">
            <Settings className="h-4 w-4 text-primary" />
            <span className="text-sm font-medium">Account Settings</span>
          </div>

          <div>
            <h1 className="text-4xl md:text-5xl font-bold text-balance mb-2">Settings</h1>
            <p className="text-muted-foreground text-lg">Manage your account and preferences</p>
          </div>
        </div>

        {/* Profile Section */}
        <Card className="p-6 glass-card mb-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
              <User className="h-5 w-5 text-primary" />
            </div>
            <div>
              <h2 className="text-xl font-semibold">Profile</h2>
              <p className="text-sm text-muted-foreground">Update your profile picture</p>
            </div>
          </div>

          <div className="space-y-6">
            {/* Profile Picture */}
            <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
              <Avatar className="h-24 w-24">
                {profilePicture ? (
                  <AvatarImage src={`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002"}${profilePicture}`} alt={username} />
                ) : (
                  <AvatarFallback className="bg-primary/10 text-primary text-2xl">
                    {username.substring(0, 2).toUpperCase()}
                  </AvatarFallback>
                )}
              </Avatar>

              <div className="flex-1 space-y-3">
                <div className="flex flex-wrap gap-2">
                  <Label htmlFor="picture-upload" className="cursor-pointer">
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      className="gap-2"
                      disabled={uploadingPicture}
                      asChild
                    >
                      <span>
                        <Upload className="h-4 w-4" />
                        {uploadingPicture ? "Uploading..." : "Upload Picture"}
                      </span>
                    </Button>
                  </Label>
                  <Input
                    id="picture-upload"
                    type="file"
                    accept="image/jpeg,image/jpg,image/png"
                    className="hidden"
                    onChange={handlePictureUpload}
                    disabled={uploadingPicture}
                  />

                  {profilePicture && (
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      className="gap-2 text-destructive hover:text-destructive"
                      onClick={handlePictureDelete}
                      disabled={uploadingPicture}
                    >
                      <Trash2 className="h-4 w-4" />
                      Delete Picture
                    </Button>
                  )}
                </div>

                <p className="text-xs text-muted-foreground">
                  JPG, JPEG, or PNG. Max size 5MB.
                </p>

                {pictureError && (
                  <div className="flex items-center gap-2 p-3 bg-destructive/10 text-destructive rounded-lg text-sm">
                    <AlertCircle className="h-4 w-4 flex-shrink-0" />
                    <span>{pictureError}</span>
                  </div>
                )}

                {pictureSuccess && (
                  <div className="flex items-center gap-2 p-3 bg-green-500/10 text-green-600 rounded-lg text-sm">
                    <CheckCircle className="h-4 w-4 flex-shrink-0" />
                    <span>{pictureSuccess}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Username and Email (read-only) */}
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="username">Username</Label>
                <Input id="username" value={username} disabled className="bg-muted/30" />
              </div>

              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input id="email" value={email} disabled className="bg-muted/30" />
              </div>
            </div>
          </div>
        </Card>

        {/* Password Section */}
        <Card className="p-6 glass-card">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
              <Lock className="h-5 w-5 text-primary" />
            </div>
            <div>
              <h2 className="text-xl font-semibold">Password</h2>
              <p className="text-sm text-muted-foreground">Change your password</p>
            </div>
          </div>

          <form onSubmit={handlePasswordChange} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="current-password">Current Password</Label>
              <Input
                id="current-password"
                type="password"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                placeholder="Enter current password"
                disabled={changingPassword}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="new-password">New Password</Label>
              <Input
                id="new-password"
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                placeholder="Enter new password (min. 6 characters)"
                disabled={changingPassword}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="confirm-password">Confirm New Password</Label>
              <Input
                id="confirm-password"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Confirm new password"
                disabled={changingPassword}
                required
              />
            </div>

            {passwordError && (
              <div className="flex items-center gap-2 p-3 bg-destructive/10 text-destructive rounded-lg text-sm">
                <AlertCircle className="h-4 w-4 flex-shrink-0" />
                <span>{passwordError}</span>
              </div>
            )}

            {passwordSuccess && (
              <div className="flex items-center gap-2 p-3 bg-green-500/10 text-green-600 rounded-lg text-sm">
                <CheckCircle className="h-4 w-4 flex-shrink-0" />
                <span>{passwordSuccess}</span>
              </div>
            )}

            <Button type="submit" className="w-full sm:w-auto" disabled={changingPassword}>
              {changingPassword ? "Changing Password..." : "Change Password"}
            </Button>
          </form>
        </Card>
      </div>
    </div>
  )
}
