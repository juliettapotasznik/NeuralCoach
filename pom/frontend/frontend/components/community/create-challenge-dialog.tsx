"use client"

import { useState } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Plus } from "lucide-react"

interface CreateChallengeDialogProps {
  onSuccess?: () => void
}

export function CreateChallengeDialog({ onSuccess }: CreateChallengeDialogProps) {
  const [open, setOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    icon: "Dumbbell",
    target: 0,
    unit: "workouts",
    reward_points: 100,
    end_date: ""
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const token = localStorage.getItem("access_token")
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002"
      const response = await fetch(`${apiUrl}/api/community/challenges/create`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
          ...formData,
          end_date: new Date(formData.end_date).toISOString()
        })
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || "Failed to create challenge")
      }

      setOpen(false)
      setFormData({
        name: "",
        description: "",
        icon: "Dumbbell",
        target: 0,
        unit: "workouts",
        reward_points: 100,
        end_date: ""
      })
      onSuccess?.()
    } catch (err) {
      console.error("Failed to create challenge:", err)
      alert(err instanceof Error ? err.message : "Failed to create challenge")
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button size="sm" className="gap-2">
          <Plus className="h-4 w-4" />
          Create Challenge
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Create New Challenge</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="name">Challenge Name</Label>
            <Input
              id="name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="e.g., 30-Day Fitness Challenge"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Describe the challenge..."
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="target">Target</Label>
              <Input
                id="target"
                type="number"
                value={formData.target}
                onChange={(e) => setFormData({ ...formData, target: parseInt(e.target.value) })}
                placeholder="e.g., 30"
                required
                min="1"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="unit">Unit</Label>
              <Select
                value={formData.unit}
                onValueChange={(value) => setFormData({ ...formData, unit: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="workouts">Workouts</SelectItem>
                  <SelectItem value="days">Days</SelectItem>
                  <SelectItem value="miles">Miles</SelectItem>
                  <SelectItem value="calories">Calories</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="icon">Icon</Label>
              <Select
                value={formData.icon}
                onValueChange={(value) => setFormData({ ...formData, icon: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Dumbbell">Dumbbell</SelectItem>
                  <SelectItem value="Flame">Flame</SelectItem>
                  <SelectItem value="Target">Target</SelectItem>
                  <SelectItem value="Trophy">Trophy</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="reward">Reward Points</Label>
              <Input
                id="reward"
                type="number"
                value={formData.reward_points}
                onChange={(e) => setFormData({ ...formData, reward_points: parseInt(e.target.value) })}
                placeholder="e.g., 100"
                required
                min="1"
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="end_date">End Date</Label>
            <Input
              id="end_date"
              type="datetime-local"
              value={formData.end_date}
              onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
              required
            />
          </div>

          <div className="flex gap-2 justify-end">
            <Button type="button" variant="outline" onClick={() => setOpen(false)} disabled={loading}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? "Creating..." : "Create Challenge"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}
