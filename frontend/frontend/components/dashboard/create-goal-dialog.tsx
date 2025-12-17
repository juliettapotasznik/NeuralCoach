"use client"

import { useState } from "react"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { apiClient } from "@/lib/api"
import { AlertCircle } from "lucide-react"

interface CreateGoalDialogProps {
  open: boolean
  onClose: () => void
  onSuccess: () => void
}

export function CreateGoalDialog({ open, onClose, onSuccess }: CreateGoalDialogProps) {
  const [title, setTitle] = useState("")
  const [targetValue, setTargetValue] = useState("")
  const [unit, setUnit] = useState("")
  const [deadline, setDeadline] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    if (!title.trim()) {
      setError("Goal title is required")
      return
    }

    const targetNum = parseInt(targetValue)
    if (isNaN(targetNum) || targetNum <= 0) {
      setError("Target value must be a positive number")
      return
    }

    if (!unit.trim()) {
      setError("Unit is required (e.g., kg, reps, minutes)")
      return
    }

    setLoading(true)

    try {
      const result = await apiClient.createGoal(title.trim(), targetNum, unit.trim(), deadline && deadline.trim() ? deadline.trim() : undefined)

      // Show success message with points
      if (result.points_earned) {
        setSuccessMessage(`Goal created! +${result.points_earned} points 🎉 (Total: ${result.total_points}, Level: ${result.level})`)
        setError(null)

        // Wait 2 seconds to show the success message before closing
        setTimeout(() => {
          setTitle("")
          setTargetValue("")
          setUnit("")
          setDeadline("")
          setSuccessMessage(null)
          onSuccess()
          onClose()
        }, 2000)
      } else {
        setTitle("")
        setTargetValue("")
        setUnit("")
        setDeadline("")
        onSuccess()
        onClose()
      }
    } catch (err) {
      console.error("Goal creation error:", err)
      const errorMsg = err instanceof Error ? err.message : (typeof err === 'object' && err !== null ? JSON.stringify(err) : "Failed to create goal")
      setError(errorMsg)
    } finally {
      setLoading(false)
    }
  }

  const handleClose = () => {
    if (!loading) {
      setTitle("")
      setTargetValue("")
      setUnit("")
      setDeadline("")
      setError(null)
      setSuccessMessage(null)
      onClose()
    }
  }

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Create New Goal</DialogTitle>
          <DialogDescription>Set a new fitness goal to track your progress</DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4 mt-4">
          <div className="space-y-2">
            <Label htmlFor="goal-title">Goal Title *</Label>
            <Input
              id="goal-title"
              placeholder="e.g., Bench Press 100kg"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              disabled={loading}
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="target-value">Target Value *</Label>
              <Input
                id="target-value"
                type="number"
                placeholder="100"
                value={targetValue}
                onChange={(e) => setTargetValue(e.target.value)}
                disabled={loading}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="unit">Unit *</Label>
              <Input
                id="unit"
                placeholder="kg, reps, min"
                value={unit}
                onChange={(e) => setUnit(e.target.value)}
                disabled={loading}
                required
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="deadline">Deadline (Optional)</Label>
            <Input
              id="deadline"
              type="date"
              value={deadline}
              onChange={(e) => setDeadline(e.target.value)}
              disabled={loading}
              min={new Date().toISOString().split("T")[0]}
            />
          </div>

          {error && (
            <div className="flex items-center gap-2 p-3 bg-destructive/10 text-destructive rounded-lg text-sm">
              <AlertCircle className="h-4 w-4 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {successMessage && (
            <div className="p-3 bg-green-500/10 text-green-600 dark:text-green-400 rounded-lg text-sm font-medium">
              {successMessage}
            </div>
          )}

          <div className="flex justify-end gap-2 pt-4">
            <Button type="button" variant="outline" onClick={handleClose} disabled={loading}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? "Creating..." : "Create Goal"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}
