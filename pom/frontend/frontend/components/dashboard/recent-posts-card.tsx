"use client"

import { useEffect, useState } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { MessageSquare, Heart, Plus, Send, Trash2 } from "lucide-react"
import { apiClient, Post, Comment } from "@/lib/api"
import { formatDistanceToNow } from "date-fns"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"

interface RecentPostsCardProps {
  onPointsEarned?: () => void
}

export function RecentPostsCard({ onPointsEarned }: RecentPostsCardProps = {}) {
  const [posts, setPosts] = useState<Post[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const [newPostContent, setNewPostContent] = useState("")
  const [creatingPost, setCreatingPost] = useState(false)
  const [showNewPost, setShowNewPost] = useState(false)

  // Comments dialog state
  const [selectedPost, setSelectedPost] = useState<Post | null>(null)
  const [comments, setComments] = useState<Comment[]>([])
  const [newComment, setNewComment] = useState("")
  const [loadingComments, setLoadingComments] = useState(false)
  const [addingComment, setAddingComment] = useState(false)

  useEffect(() => {
    loadPosts()
  }, [])

  const loadPosts = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await apiClient.getPosts(10)
      setPosts(data)
    } catch (err) {
      console.error("Failed to fetch posts:", err)
      setError(err instanceof Error ? err.message : "Failed to load posts")
    } finally {
      setLoading(false)
    }
  }

  const handleCreatePost = async () => {
    if (!newPostContent.trim()) return

    setCreatingPost(true)
    try {
      const result = await apiClient.createPost(newPostContent.trim())
      setNewPostContent("")
      setShowNewPost(false)
      await loadPosts()

      // Show points notification if points were earned
      if (result.points_earned) {
        const successMsg = `Post created! +${result.points_earned} points 🎉 (Total: ${result.total_points}, Level: ${result.level})`
        setSuccessMessage(successMsg)
        // Clear the success message after 5 seconds
        setTimeout(() => setSuccessMessage(null), 5000)

        // Notify parent component to refresh stats
        if (onPointsEarned) {
          onPointsEarned()
        }
      }
    } catch (err) {
      console.error("Failed to create post:", err)
      setError(err instanceof Error ? err.message : "Failed to create post")
    } finally {
      setCreatingPost(false)
    }
  }

  const handleLike = async (postId: number) => {
    try {
      const result = await apiClient.likePost(postId)
      setPosts(posts.map(post =>
        post.id === postId
          ? {
              ...post,
              is_liked: result.liked,
              likes_count: result.liked ? post.likes_count + 1 : post.likes_count - 1
            }
          : post
      ))
    } catch (err) {
      console.error("Failed to like post:", err)
    }
  }

  const handleShowComments = async (post: Post) => {
    setSelectedPost(post)
    setLoadingComments(true)
    try {
      const commentsData = await apiClient.getPostComments(post.id)
      setComments(commentsData)
    } catch (err) {
      console.error("Failed to load comments:", err)
    } finally {
      setLoadingComments(false)
    }
  }

  const handleAddComment = async () => {
    if (!selectedPost || !newComment.trim()) return

    setAddingComment(true)
    try {
      await apiClient.addComment(selectedPost.id, newComment.trim())
      setNewComment("")
      // Reload comments
      const commentsData = await apiClient.getPostComments(selectedPost.id)
      setComments(commentsData)
      // Update comment count
      setPosts(posts.map(post =>
        post.id === selectedPost.id
          ? { ...post, comments_count: post.comments_count + 1 }
          : post
      ))
    } catch (err) {
      console.error("Failed to add comment:", err)
    } finally {
      setAddingComment(false)
    }
  }

  const handleDeletePost = async (postId: number) => {
    if (!confirm("Are you sure you want to delete this post?")) return

    try {
      await apiClient.deletePost(postId)
      setPosts(posts.filter(post => post.id !== postId))
    } catch (err) {
      console.error("Failed to delete post:", err)
      setError(err instanceof Error ? err.message : "Failed to delete post")
    }
  }

  return (
    <>
      <Card className="p-6 glass-card">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
              <MessageSquare className="h-5 w-5 text-primary" />
            </div>
            <div>
              <h2 className="text-xl font-semibold">Recent Posts</h2>
              <p className="text-sm text-muted-foreground">Your activity feed</p>
            </div>
          </div>
          <Button
            size="sm"
            className="gap-2 bg-primary hover:bg-primary/90 text-primary-foreground"
            onClick={() => setShowNewPost(!showNewPost)}
          >
            <Plus className="h-4 w-4" />
            New Post
          </Button>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-destructive/10 text-destructive rounded-lg text-sm">
            {error}
          </div>
        )}

        {successMessage && (
          <div className="mb-4 p-3 bg-green-500/10 text-green-600 dark:text-green-400 rounded-lg text-sm font-medium">
            {successMessage}
          </div>
        )}

        {/* New Post Form */}
        {showNewPost && (
          <div className="mb-6 p-4 rounded-lg border border-border/50 bg-muted/30">
            <Textarea
              placeholder="What's on your mind?"
              value={newPostContent}
              onChange={(e) => setNewPostContent(e.target.value)}
              className="mb-3"
              rows={3}
            />
            <div className="flex justify-end gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  setShowNewPost(false)
                  setNewPostContent("")
                }}
                disabled={creatingPost}
              >
                Cancel
              </Button>
              <Button
                size="sm"
                onClick={handleCreatePost}
                disabled={creatingPost || !newPostContent.trim()}
              >
                {creatingPost ? "Posting..." : "Post"}
              </Button>
            </div>
          </div>
        )}

        {loading ? (
          <div className="text-center py-8 text-muted-foreground">Loading posts...</div>
        ) : posts.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            No posts yet. Be the first to share something!
          </div>
        ) : (
          <div className="space-y-4">
            {posts.map((post) => (
              <div
                key={post.id}
                className="p-4 rounded-lg border border-border/50 hover:border-primary/30 transition-colors"
              >
                <div className="flex gap-3">
                  <Avatar className="h-10 w-10">
                    <AvatarFallback className="bg-primary/10 text-primary text-sm">
                      {post.avatar}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-2 mb-2">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-sm">{post.username}</span>
                        <span className="text-xs text-muted-foreground">
                          {formatDistanceToNow(new Date(post.created_at), { addSuffix: true })}
                        </span>
                      </div>
                      {/* Show delete button for own posts */}
                    </div>
                    <p className="text-sm leading-relaxed mb-3 whitespace-pre-wrap">{post.content}</p>
                    <div className="flex items-center gap-4">
                      <Button
                        variant="ghost"
                        size="sm"
                        className={`h-8 gap-2 ${post.is_liked ? 'text-red-500' : 'text-muted-foreground hover:text-primary'}`}
                        onClick={() => handleLike(post.id)}
                      >
                        <Heart className={`h-4 w-4 ${post.is_liked ? 'fill-current' : ''}`} />
                        <span className="text-xs">{post.likes_count}</span>
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-8 gap-2 text-muted-foreground hover:text-primary"
                        onClick={() => handleShowComments(post)}
                      >
                        <MessageSquare className="h-4 w-4" />
                        <span className="text-xs">{post.comments_count}</span>
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>

      {/* Comments Dialog */}
      <Dialog open={!!selectedPost} onOpenChange={() => setSelectedPost(null)}>
        <DialogContent className="sm:max-w-[600px]">
          <DialogHeader>
            <DialogTitle>Comments</DialogTitle>
          </DialogHeader>

          <div className="space-y-4 max-h-[400px] overflow-y-auto">
            {loadingComments ? (
              <div className="text-center py-8 text-muted-foreground">Loading comments...</div>
            ) : comments.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                No comments yet. Be the first to comment!
              </div>
            ) : (
              comments.map((comment) => (
                <div key={comment.id} className="flex gap-3">
                  <Avatar className="h-8 w-8">
                    <AvatarFallback className="bg-primary/10 text-primary text-xs">
                      {comment.avatar}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-semibold text-sm">{comment.username}</span>
                      <span className="text-xs text-muted-foreground">
                        {formatDistanceToNow(new Date(comment.created_at), { addSuffix: true })}
                      </span>
                    </div>
                    <p className="text-sm">{comment.content}</p>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Add Comment */}
          <div className="flex gap-2 pt-4 border-t">
            <Textarea
              placeholder="Write a comment..."
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
              rows={2}
              className="flex-1"
            />
            <Button
              size="sm"
              onClick={handleAddComment}
              disabled={addingComment || !newComment.trim()}
              className="self-end"
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </>
  )
}
