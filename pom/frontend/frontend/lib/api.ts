const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002"

export interface RegisterData {
  email: string
  username: string
  password: string
}

export interface LoginData {
  username: string
  password: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

export interface UserResponse {
  id: number
  email: string
  username: string
  is_verified: boolean
  profile_picture: string | null
  created_at: string
}

export interface ApiError {
  detail: string
}

export interface AnalysisResponse {
  status: string
  feedback: string
  processing_time: number
  joint_ratings?: Record<string, number>
  avg_rating?: string
  analysis_id?: number
  overlay_video_url?: string
  processed_video_url?: string
}

export interface LeaderboardUser {
  rank: number
  name: string
  points: number
  workouts: number
  avatar: string
  trend: string
}

export interface Challenge {
  id: number
  name: string
  description: string
  icon: string
  participants: number
  progress: number
  target: number
  unit: string
  reward: number
  timeLeft: string
  joined: boolean
}

export interface Friend {
  id: number
  name: string
  status: string | null
  avatar: string
  online: boolean
  unread_count: number
}

export interface SuggestedUser {
  id: number
  name: string
  bio: string | null
  avatar: string
  level: number
  mutualFriends: number
}

export interface SearchedUser {
  id: number
  username: string
  avatar: string
  level: number
  is_friend: boolean
  has_pending_request: boolean
}

export interface FriendRequest {
  id: number
  user_id: number
  username: string
  avatar: string
  created_at: string
}

export interface Message {
  id: number
  sender_id: number
  sender_name: string
  recipient_id: number
  recipient_name: string
  content: string
  is_read: boolean
  created_at: string
}

export interface UserStats {
  username: string
  level: number
  points: number
  current_streak: number
  workouts_this_week: number
  workouts_this_month: number
  total_workouts: number
}

export interface Achievement {
  id: number
  name: string
  description: string
  icon: string
  category: string
  unlocked: boolean
  unlocked_at: string | null
  progress: number
  requirement: number
}

export interface Goal {
  id: number
  title: string
  target_value: number
  current_value: number
  unit: string
  deadline: string | null
  completed: boolean
  completed_at: string | null
  progress_percentage: number
}

export interface RecentWorkout {
  id: number
  exercise_name: string
  avg_rating: number | null
  created_at: string
}

export interface Post {
  id: number
  user_id: number
  username: string
  avatar: string
  content: string
  likes_count: number
  comments_count: number
  is_liked: boolean
  created_at: string
}

export interface Comment {
  id: number
  user_id: number
  username: string
  avatar: string
  content: string
  created_at: string
}

export interface DietPlanResponse {
  nutrition: {
    calories: number
    protein: number
    carbs: number
    fat: number
  }
  meal_plan: Array<{
    meal_type: string
    recipes: any[]
  }>
  generated_at: string
  cached: boolean
}

class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl
  }

  private getAuthHeaders(): HeadersInit {
    const token = localStorage.getItem("access_token")
    if (token) {
      return {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      }
    }
    return {
      "Content-Type": "application/json",
    }
  }
  async addFriend(userId: number): Promise<{ message: string }> {
  const response = await fetch(`${this.baseUrl}/api/community/friends/${userId}/add`, {
    method: "POST",
    headers: this.getAuthHeaders(),
  })

  if (!response.ok) {
    let msg = "Failed to send friend request"

    try {
      const data = await response.json()
      console.log("addFriend error body:", data) // pomoże zobaczyć co dokładnie zwraca backend

      if (data?.detail) {
        if (typeof data.detail === "string") {
          msg = data.detail
        } else {
          // gdy detail jest obiektem / tablicą – zrób z tego tekst
          msg = JSON.stringify(data.detail)
        }
      }
    } catch (e) {
      console.error("Error parsing addFriend error response:", e)
    }

    throw new Error(msg)
  }

  return response.json()
}



  async register(data: RegisterData): Promise<UserResponse> {
    console.log('Registration data being sent:', data)
    const response = await fetch(`${this.baseUrl}/api/users/register`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    })

    if (!response.ok) {
      const error: ApiError = await response.json()
      console.error('Registration error:', error)
      throw new Error(error.detail || "Registration failed")
    }

    return response.json()
  }

  async login(data: LoginData): Promise<TokenResponse> {
    const response = await fetch(`${this.baseUrl}/api/users/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    })

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Login failed")
    }

    const tokenData: TokenResponse = await response.json()

    // Store token in localStorage
    localStorage.setItem("access_token", tokenData.access_token)

    return tokenData
  }

  async getCurrentUser(): Promise<UserResponse> {
    const response = await fetch(`${this.baseUrl}/api/users/me`, {
      method: "GET",
      headers: this.getAuthHeaders(),
    })

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to fetch user data")
    }

    return response.json()
  }

  logout(): void {
    localStorage.removeItem("access_token")
  }

  isAuthenticated(): boolean {
    return !!localStorage.getItem("access_token")
  }

  getToken(): string | null {
    return localStorage.getItem("access_token")
  }

  async changePassword(currentPassword: string, newPassword: string): Promise<{ message: string }> {
    const response = await fetch(`${this.baseUrl}/api/users/change-password`, {
      method: "POST",
      headers: this.getAuthHeaders(),
      body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
    })

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to change password")
    }

    return response.json()
  }

  async uploadProfilePicture(file: File): Promise<UserResponse> {
    const formData = new FormData()
    formData.append("file", file)

    const token = this.getToken()
    const headers: HeadersInit = {}
    if (token) {
      headers.Authorization = `Bearer ${token}`
    }

    const response = await fetch(`${this.baseUrl}/api/users/upload-profile-picture`, {
      method: "POST",
      headers,
      body: formData,
    })

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to upload profile picture")
    }

    return response.json()
  }

  async deleteProfilePicture(): Promise<{ message: string }> {
    const response = await fetch(`${this.baseUrl}/api/users/profile-picture`, {
      method: "DELETE",
      headers: this.getAuthHeaders(),
    })

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to delete profile picture")
    }

    return response.json()
  }

  async analyzeExercise(videoFile: File, exerciseName: string): Promise<AnalysisResponse> {
    const formData = new FormData()
    formData.append("file", videoFile)
    formData.append("exercise_name", exerciseName)

    const token = this.getToken()
    const headers: HeadersInit = {}
    if (token) {
      headers.Authorization = `Bearer ${token}`
    }

    const response = await fetch(`${this.baseUrl}/analyze_exercise`, {
      method: "POST",
      headers,
      body: formData,
    })

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Analysis failed")
    }

    return response.json()
  }

  // Community API methods
  async getWeeklyLeaderboard(limit: number = 10): Promise<LeaderboardUser[]> {
    const response = await fetch(`${this.baseUrl}/api/community/leaderboard/weekly?limit=${limit}`, {
      method: "GET",
      headers: this.getAuthHeaders(),
    })

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to fetch weekly leaderboard")
    }

    return response.json()
  }

  async getMonthlyLeaderboard(limit: number = 10): Promise<LeaderboardUser[]> {
    const response = await fetch(`${this.baseUrl}/api/community/leaderboard/monthly?limit=${limit}`, {
      method: "GET",
      headers: this.getAuthHeaders(),
    })

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to fetch monthly leaderboard")
    }

    return response.json()
  }

  async getChallenges(): Promise<Challenge[]> {
    const response = await fetch(`${this.baseUrl}/api/community/challenges`, {
      method: "GET",
      headers: this.getAuthHeaders(),
    })

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to fetch challenges")
    }

    return response.json()
  }

  async joinChallenge(challengeId: number): Promise<{ message: string; points_earned?: number; total_points?: number; level?: number }> {
    const response = await fetch(`${this.baseUrl}/api/community/challenges/${challengeId}/join`, {
      method: "POST",
      headers: this.getAuthHeaders(),
    })

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to join challenge")
    }

    return response.json()
  }

  async updateChallengeProgress(challengeId: number, progress: number): Promise<{ message: string; progress: number; completed: boolean }> {
    const response = await fetch(`${this.baseUrl}/api/community/challenges/${challengeId}/progress`, {
      method: "PATCH",
      headers: this.getAuthHeaders(),
      body: JSON.stringify({ progress }),
    })

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to update challenge progress")
    }

    return response.json()
  }

  async getFriends(): Promise<Friend[]> {
    const response = await fetch(`${this.baseUrl}/api/community/friends`, {
      method: "GET",
      headers: this.getAuthHeaders(),
    })

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to fetch friends")
    }

    return response.json()
  }

  async getSuggestedUsers(limit: number = 5): Promise<SuggestedUser[]> {
    const response = await fetch(`${this.baseUrl}/api/community/suggested?limit=${limit}`, {
      method: "GET",
      headers: this.getAuthHeaders(),
    })

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to fetch suggested users")
    }

    return response.json()
  }

  async searchUsers(query: string, limit: number = 10): Promise<SearchedUser[]> {
    const response = await fetch(`${this.baseUrl}/api/community/users/search?query=${encodeURIComponent(query)}&limit=${limit}`, {
      method: "GET",
      headers: this.getAuthHeaders(),
    })

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to search users")
    }

    return response.json()
  }

  // Friend requests
  async getFriendRequests(): Promise<FriendRequest[]> {
    const response = await fetch(`${this.baseUrl}/api/community/friends/requests`, {
      method: "GET",
      headers: this.getAuthHeaders(),
    })

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to fetch friend requests")
    }

    return response.json()
  }

  async acceptFriendRequest(friendshipId: number): Promise<{ message: string }> {
    const response = await fetch(`${this.baseUrl}/api/community/friends/${friendshipId}/accept`, {
      method: "POST",
      headers: this.getAuthHeaders(),
    })

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to accept friend request")
    }

    return response.json()
  }

  async rejectFriendRequest(friendshipId: number): Promise<{ message: string }> {
    const response = await fetch(`${this.baseUrl}/api/community/friends/${friendshipId}/reject`, {
      method: "POST",
      headers: this.getAuthHeaders(),
    })

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to reject friend request")
    }

    return response.json()
  }

  // Messages
  async sendMessage(recipientId: number, content: string): Promise<{ message: string; message_id: number }> {
    const response = await fetch(`${this.baseUrl}/api/community/messages/send`, {
      method: "POST",
      headers: this.getAuthHeaders(),
      body: JSON.stringify({ recipient_id: recipientId, content }),
    })

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to send message")
    }

    return response.json()
  }

  async getConversation(friendId: number, limit: number = 50): Promise<Message[]> {
    const response = await fetch(`${this.baseUrl}/api/community/messages/${friendId}?limit=${limit}`, {
      method: "GET",
      headers: this.getAuthHeaders(),
    })

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to fetch conversation")
    }

    return response.json()
  }

  async getUnreadCount(): Promise<{ unread_count: number }> {
    const response = await fetch(`${this.baseUrl}/api/community/messages/unread/count`, {
      method: "GET",
      headers: this.getAuthHeaders(),
    })

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to fetch unread count")
    }

    return response.json()
  }

  // Dashboard
  async getUserStats(): Promise<UserStats> {
    const response = await fetch(`${this.baseUrl}/api/dashboard/stats`, {
      method: "GET",
      headers: this.getAuthHeaders(),
    })

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to fetch user stats")
    }

    return response.json()
  }

  async getAchievements(): Promise<Achievement[]> {
    const response = await fetch(`${this.baseUrl}/api/dashboard/achievements`, {
      method: "GET",
      headers: this.getAuthHeaders(),
    })

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to fetch achievements")
    }

    return response.json()
  }

  async getGoals(): Promise<Goal[]> {
    const response = await fetch(`${this.baseUrl}/api/dashboard/goals`, {
      method: "GET",
      headers: this.getAuthHeaders(),
    })

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to fetch goals")
    }

    return response.json()
  }

  async getRecentWorkouts(limit: number = 10): Promise<RecentWorkout[]> {
    const response = await fetch(`${this.baseUrl}/api/dashboard/recent-workouts?limit=${limit}`, {
      method: "GET",
      headers: this.getAuthHeaders(),
    })

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to fetch recent workouts")
    }

    return response.json()
  }

  async createGoal(title: string, targetValue: number, unit: string, deadline?: string): Promise<{ message: string; goal_id: number; points_earned?: number; total_points?: number; level?: number }> {
    const requestBody = { title, target_value: targetValue, unit, deadline }
    console.log("Creating goal with data:", requestBody)
    const response = await fetch(`${this.baseUrl}/api/dashboard/goals/create`, {
      method: "POST",
      headers: this.getAuthHeaders(),
      body: JSON.stringify(requestBody),
    })

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to create goal")
    }

    return response.json()
  }

  async completeGoal(goalId: number): Promise<{ message: string; points_earned?: number; total_points?: number; level?: number }> {
    const response = await fetch(`${this.baseUrl}/api/dashboard/goals/${goalId}/complete`, {
      method: "POST",
      headers: this.getAuthHeaders(),
    })

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to complete goal")
    }

    return response.json()
  }

  // Posts
  async getPosts(limit: number = 20, offset: number = 0): Promise<Post[]> {
    const response = await fetch(`${this.baseUrl}/api/community/posts?limit=${limit}&offset=${offset}`, {
      method: "GET",
      headers: this.getAuthHeaders(),
    })

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to fetch posts")
    }

    return response.json()
  }

  async createPost(content: string): Promise<{ message: string; post_id: number; points_earned?: number; total_points?: number; level?: number }> {
    const response = await fetch(`${this.baseUrl}/api/community/posts`, {
      method: "POST",
      headers: this.getAuthHeaders(),
      body: JSON.stringify({ content }),
    })

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to create post")
    }

    return response.json()
  }

  async likePost(postId: number): Promise<{ message: string; liked: boolean }> {
    const response = await fetch(`${this.baseUrl}/api/community/posts/${postId}/like`, {
      method: "POST",
      headers: this.getAuthHeaders(),
    })

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to like post")
    }

    return response.json()
  }

  async getPostComments(postId: number): Promise<Comment[]> {
    const response = await fetch(`${this.baseUrl}/api/community/posts/${postId}/comments`, {
      method: "GET",
      headers: this.getAuthHeaders(),
    })

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to fetch comments")
    }

    return response.json()
  }

  async addComment(postId: number, content: string): Promise<{ message: string; comment_id: number }> {
    const response = await fetch(`${this.baseUrl}/api/community/posts/${postId}/comments`, {
      method: "POST",
      headers: this.getAuthHeaders(),
      body: JSON.stringify({ content }),
    })

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to add comment")
    }

    return response.json()
  }

  async deletePost(postId: number): Promise<{ message: string }> {
    const response = await fetch(`${this.baseUrl}/api/community/posts/${postId}`, {
      method: "DELETE",
      headers: this.getAuthHeaders(),
    })

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to delete post")
    }

    return response.json()
  }

  // Diet Plans
  async getCurrentDietPlan(): Promise<DietPlanResponse> {
    const response = await fetch(`${this.baseUrl}/api/diet/current`, {
      method: "GET",
      headers: this.getAuthHeaders(),
    })

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to fetch diet plan")
    }

    return response.json()
  }

  // Workout Plans
  async getCurrentWorkoutPlan(): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/dashboard/workout-plans/current`, {
      method: "GET",
      headers: this.getAuthHeaders(),
    })

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to fetch workout plan")
    }

    return response.json()
  }

  async getCompletedExercises(planId: number): Promise<{ completed_indices: number[] }> {
    const response = await fetch(`${this.baseUrl}/api/dashboard/workout-plans/${planId}/completed-exercises`, {
      method: "GET",
      headers: this.getAuthHeaders(),
    })

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to fetch completed exercises")
    }

    return response.json()
  }

  async markExerciseComplete(planId: number, exerciseIndex: number): Promise<{ message: string; points_earned?: number; total_points?: number; level?: number }> {
    const response = await fetch(`${this.baseUrl}/api/dashboard/workout-plans/${planId}/exercises/complete`, {
      method: "POST",
      headers: this.getAuthHeaders(),
      body: JSON.stringify({ exercise_index: exerciseIndex }),
    })

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to mark exercise complete")
    }

    return response.json()
  }

  async getCompletedMeals(): Promise<{
    completed_meals: Array<{ meal_type: string; recipe_index: number; completed_at: string }>
    nutrition_consumed: { calories: number; protein: number; carbs: number; fat: number }
  }> {
    const response = await fetch(`${this.baseUrl}/api/dashboard/diet-plans/current/completed-meals`, {
      method: "GET",
      headers: this.getAuthHeaders(),
    })

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to fetch completed meals")
    }

    return response.json()
  }

  async markMealComplete(mealType: string, recipeIndex: number): Promise<{ message: string; points_earned?: number; total_points?: number; level?: number }> {
    const response = await fetch(`${this.baseUrl}/api/dashboard/diet-plans/current/meals/complete`, {
      method: "POST",
      headers: this.getAuthHeaders(),
      body: JSON.stringify({ meal_type: mealType, recipe_index: recipeIndex }),
    })

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to mark meal complete")
    }

    return response.json()
  }

  async createWorkoutPlan(planName: string, exercises: any[]): Promise<{ message: string; plan_id: number }> {
    const response = await fetch(`${this.baseUrl}/api/dashboard/workout-plans/create`, {
      method: "POST",
      headers: this.getAuthHeaders(),
      body: JSON.stringify({ plan_name: planName, exercises }),
    })

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to create workout plan")
    }

    return response.json()
  }

  // Exercise Catalog
  async getExercises(params?: { limit?: number; offset?: number; body_part?: string; analyzable?: boolean }): Promise<{
    total: number
    exercises: Array<{
      id: number
      name: string
      media_file: string
      media_url: string
      attribution: string
      description: string
      is_analyzable: boolean
      body_parts: Array<{ id: number; name: string }>
    }>
  }> {
    const queryParams = new URLSearchParams()
    if (params?.limit) queryParams.append("limit", params.limit.toString())
    if (params?.offset) queryParams.append("offset", params.offset.toString())
    if (params?.body_part) queryParams.append("body_part", params.body_part)
    if (params?.analyzable !== undefined) queryParams.append("analyzable", params.analyzable.toString())

    const response = await fetch(`${this.baseUrl}/api/exercises/list?${queryParams}`, {
      method: "GET",
      headers: this.getAuthHeaders(),
    })

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to fetch exercises")
    }

    return response.json()
  }

  async getExerciseCatalog(search?: string): Promise<{
    total: number
    exercises: Array<{
      id: number
      name: string
      media_file: string
      media_url: string
      attribution: string
      description: string
      is_analyzable: boolean
      body_parts: Array<{ id: number; name: string }>
    }>
  }> {
    const queryParams = new URLSearchParams()
    if (search) queryParams.append("search", search)

    const response = await fetch(`${this.baseUrl}/api/exercises/catalog?${queryParams}`, {
      method: "GET",
      headers: this.getAuthHeaders(),
    })

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to fetch exercise catalog")
    }

    return response.json()
  }
}

export const apiClient = new ApiClient(API_BASE_URL)
