"use client"

import { useState } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Play, Pause, Info } from "lucide-react"
import Image from "next/image"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"

interface Exercise {
  id: number
  name: string
  media_file: string
  media_url: string
  attribution: string
  description: string
  is_analyzable: boolean
  body_parts: Array<{ id: number; name: string }>
}

interface ExerciseCardProps {
  exercise: Exercise
}

export function ExerciseCard({ exercise }: ExerciseCardProps) {
  const [isPlaying, setIsPlaying] = useState(false)
  const [dialogOpen, setDialogOpen] = useState(false)

  const isGif = exercise.media_file.endsWith(".gif")
  const isVideo = exercise.media_file.endsWith(".mp4") || exercise.media_file.endsWith(".webm")

  const handlePlayPause = (e: React.MouseEvent) => {
    e.stopPropagation()
    setIsPlaying(!isPlaying)
  }

  return (
    <>
      <Card className="p-4 glass-card hover:border-primary/50 transition-all group">
        {/* Media Container */}
        <div className="relative aspect-square rounded-lg overflow-hidden bg-muted mb-4">
          {isGif ? (
            <Image
              src={exercise.media_url}
              alt={exercise.name}
              fill
              className="object-cover"
              unoptimized
            />
          ) : isVideo ? (
            <video
              src={exercise.media_url}
              loop
              muted
              playsInline
              autoPlay={isPlaying}
              className="w-full h-full object-cover"
            />
          ) : (
            <Image
              src={exercise.media_url}
              alt={exercise.name}
              fill
              className="object-cover"
            />
          )}

          {/* Overlay with play button for videos */}
          {isVideo && (
            <div
              className="absolute inset-0 bg-black/30 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center cursor-pointer"
              onClick={handlePlayPause}
            >
              <Button
                size="icon"
                variant="secondary"
                className="h-12 w-12 rounded-full bg-white/90 hover:bg-white"
              >
                {isPlaying ? (
                  <Pause className="h-6 w-6 text-black" />
                ) : (
                  <Play className="h-6 w-6 text-black" />
                )}
              </Button>
            </div>
          )}

        </div>

        {/* Exercise Info */}
        <div className="space-y-3">
          <h3 className="font-semibold text-lg line-clamp-2 group-hover:text-primary transition-colors">
            {exercise.name}
          </h3>

          {/* Body Parts */}
          <div className="flex flex-wrap gap-1">
            {exercise.body_parts.map((bp) => (
              <Badge key={bp.id} variant="outline" className="text-xs">
                {bp.name}
              </Badge>
            ))}
          </div>

          {/* Description Preview */}
          <p className="text-sm text-muted-foreground line-clamp-2">
            {exercise.description}
          </p>

          {/* View Details Button */}
          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger asChild>
              <Button variant="outline" className="w-full gap-2" size="sm">
                <Info className="h-4 w-4" />
                View Details
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle className="text-2xl">{exercise.name}</DialogTitle>
                <DialogDescription>
                  {exercise.body_parts.map(bp => bp.name).join(", ")}
                </DialogDescription>
              </DialogHeader>

              <div className="space-y-4">
                {/* Large Media Display */}
                <div className="relative aspect-video rounded-lg overflow-hidden bg-muted">
                  {isGif ? (
                    <Image
                      src={exercise.media_url}
                      alt={exercise.name}
                      fill
                      className="object-contain"
                      unoptimized
                    />
                  ) : isVideo ? (
                    <video
                      src={exercise.media_url}
                      loop
                      muted
                      playsInline
                      autoPlay
                      className="w-full h-full object-contain"
                    />
                  ) : (
                    <Image
                      src={exercise.media_url}
                      alt={exercise.name}
                      fill
                      className="object-contain"
                    />
                  )}
                </div>

                {/* Description */}
                <div>
                  <h4 className="font-semibold mb-2">Description</h4>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    {exercise.description}
                  </p>
                </div>

                {/* Body Parts */}
                <div>
                  <h4 className="font-semibold mb-2">Target Muscles</h4>
                  <div className="flex flex-wrap gap-2">
                    {exercise.body_parts.map((bp) => (
                      <Badge key={bp.id} variant="secondary">
                        {bp.name}
                      </Badge>
                    ))}
                  </div>
                </div>

                {/* Attribution */}
                {exercise.attribution && (
                  <div className="text-xs text-muted-foreground border-t pt-4">
                    {exercise.attribution}
                  </div>
                )}
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </Card>
    </>
  )
}
