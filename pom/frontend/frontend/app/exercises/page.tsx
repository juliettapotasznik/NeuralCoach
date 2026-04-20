"use client"

import { useEffect, useState } from "react"
import { Navigation } from "@/components/navigation"
import { ExerciseCard } from "@/components/exercises/exercise-card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Dumbbell, Search, Filter } from "lucide-react"
import { apiClient } from "@/lib/api"

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

export default function ExerciseCatalogPage() {
  const [exercises, setExercises] = useState<Exercise[]>([])
  const [filteredExercises, setFilteredExercises] = useState<Exercise[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedBodyPart, setSelectedBodyPart] = useState<string>("all")
  const [bodyParts, setBodyParts] = useState<string[]>([])

  useEffect(() => {
    loadExercises()
  }, [])

  useEffect(() => {
    filterExercises()
  }, [searchTerm, selectedBodyPart, exercises])

  const loadExercises = async () => {
    try {
      setLoading(true)
      const data = await apiClient.getExerciseCatalog()
      setExercises(data.exercises)

      // Extract unique body parts
      const parts = new Set<string>()
      data.exercises.forEach((exercise: Exercise) => {
        exercise.body_parts.forEach(bp => parts.add(bp.name))
      })
      setBodyParts(Array.from(parts).sort())
    } catch (err) {
      console.error("Failed to load exercises:", err)
    } finally {
      setLoading(false)
    }
  }

  const filterExercises = () => {
    let filtered = exercises

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(ex =>
        ex.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        ex.description.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    // Filter by body part
    if (selectedBodyPart && selectedBodyPart !== "all") {
      filtered = filtered.filter(ex =>
        ex.body_parts.some(bp => bp.name === selectedBodyPart)
      )
    }

    setFilteredExercises(filtered)
  }

  return (
    <div className="min-h-screen">
      <Navigation />

      <div className="container mx-auto px-4 py-12">
        {/* Header */}
        <div className="mb-8 space-y-4">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-card border border-primary/20">
            <Dumbbell className="h-4 w-4 text-primary" />
            <span className="text-sm font-medium">Exercise Library</span>
          </div>

          <div>
            <h1 className="text-4xl md:text-5xl font-bold text-balance mb-2">
              <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                Exercise Catalog
              </span>
            </h1>
            <p className="text-muted-foreground text-lg">
              Browse our comprehensive library of exercises with animations
            </p>
          </div>
        </div>

        {/* Filters */}
        <div className="mb-8 flex flex-col md:flex-row gap-4">
          {/* Search */}
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              type="text"
              placeholder="Search exercises..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 glass-card"
            />
          </div>

          {/* Body Part Filter */}
          <Select value={selectedBodyPart} onValueChange={setSelectedBodyPart}>
            <SelectTrigger className="w-full md:w-[200px] glass-card">
              <div className="flex items-center gap-2">
                <Filter className="h-4 w-4" />
                <SelectValue placeholder="Body Part" />
              </div>
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Body Parts</SelectItem>
              {bodyParts.map((part) => (
                <SelectItem key={part} value={part}>
                  {part}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Results Count */}
        <div className="mb-4 text-sm text-muted-foreground">
          Showing {filteredExercises.length} of {exercises.length} exercises
        </div>

        {/* Exercise Grid */}
        {loading ? (
          <div className="text-center py-20">
            <div className="inline-flex items-center gap-3">
              <div className="h-8 w-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
              <span className="text-muted-foreground">Loading exercises...</span>
            </div>
          </div>
        ) : filteredExercises.length === 0 ? (
          <div className="text-center py-20">
            <div className="w-16 h-16 rounded-full bg-muted flex items-center justify-center mx-auto mb-4">
              <Dumbbell className="h-8 w-8 text-muted-foreground" />
            </div>
            <h3 className="text-xl font-semibold mb-2">No exercises found</h3>
            <p className="text-muted-foreground">Try adjusting your search or filters</p>
          </div>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {filteredExercises.map((exercise) => (
              <ExerciseCard key={exercise.id} exercise={exercise} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
