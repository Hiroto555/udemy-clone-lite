'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import api from '@/lib/api'
import { useAuth } from '@/contexts/auth'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Clock, Users, Award, BookOpen, Play, CheckCircle, Star } from 'lucide-react'

interface Course {
  id: string
  title: string
  description: string
  instructor_name: string
  price: number
  duration_hours: number
  level: string
  enrolled_count: number
  sections: Section[]
  average_rating?: number
  tags?: { id: string; name: string; slug: string }[]
}

interface Review {
  id: string
  rating: number
  comment?: string
  created_at: string
  user: {
    id: string
    full_name: string
  }
}

interface Section {
  id: string
  title: string
  order_index: number
  lessons: Lesson[]
}

interface Lesson {
  id: string
  title: string
  duration_minutes: number
  order_index: number
  is_preview: boolean
}

export default function CourseDetailPage() {
  const params = useParams()
  const router = useRouter()
  const { user } = useAuth()
  const [course, setCourse] = useState<Course | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [enrolling, setEnrolling] = useState(false)
  const [reviews, setReviews] = useState<Review[]>([])
  const [userReview, setUserReview] = useState({ rating: 0, comment: '' })
  const [submittingReview, setSubmittingReview] = useState(false)
  const [isEnrolled, setIsEnrolled] = useState(false)

  useEffect(() => {
    if (params.id) {
      loadCourse(params.id as string)
      loadReviews(params.id as string)
      checkEnrollment(params.id as string)
    }
  }, [params.id, user])

  const loadCourse = async (id: string) => {
    try {
      const data = await api.getCourse(id)
      setCourse(data)
    } catch (err) {
      setError('コースの読み込みに失敗しました')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const loadReviews = async (id: string) => {
    try {
      const data = await api.getReviews(id)
      setReviews(data)
    } catch (err) {
      console.error('Failed to load reviews:', err)
    }
  }

  const checkEnrollment = async (courseId: string) => {
    if (!user) return
    try {
      const enrollments = await api.getEnrolledCourses()
      setIsEnrolled(enrollments.some((e: any) => e.course.id === parseInt(courseId)))
    } catch (err) {
      console.error('Failed to check enrollment:', err)
    }
  }

  const handleSubmitReview = async () => {
    if (!user || !course || !userReview.rating) return
    
    setSubmittingReview(true)
    try {
      await api.createReview(course.id, userReview.rating, userReview.comment)
      await loadReviews(course.id)
      setUserReview({ rating: 0, comment: '' })
      alert('レビューを投稿しました')
    } catch (err) {
      console.error('Failed to submit review:', err)
      alert('レビューの投稿に失敗しました')
    } finally {
      setSubmittingReview(false)
    }
  }

  const renderStars = (rating: number, interactive = false) => {
    return (
      <div className="flex gap-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <Star
            key={star}
            className={`h-5 w-5 ${
              star <= rating ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'
            } ${interactive ? 'cursor-pointer hover:text-yellow-400' : ''}`}
            onClick={() => interactive && setUserReview({ ...userReview, rating: star })}
          />
        ))}
      </div>
    )
  }

  const handleEnroll = async () => {
    if (!user) {
      router.push('/login')
      return
    }

    setEnrolling(true)
    try {
      await api.request(`/courses/${course?.id}/enroll`, { method: 'POST' })
      router.push('/dashboard')
    } catch (err) {
      console.error('Enrollment failed:', err)
      alert('登録に失敗しました')
    } finally {
      setEnrolling(false)
    }
  }

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">読み込み中...</div>
      </div>
    )
  }

  if (error || !course) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center text-red-500">{error || 'コースが見つかりません'}</div>
      </div>
    )
  }

  const totalLessons = course.sections.reduce((acc, section) => acc + section.lessons.length, 0)

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <h1 className="text-4xl font-bold mb-4">{course.title}</h1>
          <p className="text-lg text-muted-foreground mb-6">{course.description}</p>
          
          <div className="flex flex-wrap gap-4 mb-4">
            <div className="flex items-center gap-2">
              <Award className="h-5 w-5 text-muted-foreground" />
              <span>講師: {course.instructor_name}</span>
            </div>
            <div className="flex items-center gap-2">
              <Clock className="h-5 w-5 text-muted-foreground" />
              <span>{course.duration_hours}時間</span>
            </div>
            <div className="flex items-center gap-2">
              <Users className="h-5 w-5 text-muted-foreground" />
              <span>{course.enrolled_count}人が受講中</span>
            </div>
            <div className="flex items-center gap-2">
              <BookOpen className="h-5 w-5 text-muted-foreground" />
              <span>{totalLessons}レッスン</span>
            </div>
            {course.average_rating && (
              <div className="flex items-center gap-2">
                {renderStars(Math.round(course.average_rating))}
                <span>{course.average_rating.toFixed(1)} ({reviews.length}件のレビュー)</span>
              </div>
            )}
          </div>

          {course.tags && course.tags.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-8">
              {course.tags.map((tag) => (
                <span
                  key={tag.id}
                  className="px-3 py-1 bg-secondary text-secondary-foreground rounded-full text-sm"
                >
                  {tag.name}
                </span>
              ))}
            </div>
          )}

          <div className="space-y-4">
            <h2 className="text-2xl font-semibold">コース内容</h2>
            {course.sections.map((section, sectionIndex) => (
              <Card key={section.id}>
                <CardHeader>
                  <CardTitle className="text-lg">
                    セクション {sectionIndex + 1}: {section.title}
                  </CardTitle>
                  <CardDescription>
                    {section.lessons.length}レッスン
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {section.lessons.map((lesson, lessonIndex) => (
                      <li key={lesson.id} className="flex items-center justify-between py-2">
                        <div className="flex items-center gap-3">
                          <Play className="h-4 w-4 text-muted-foreground" />
                          <span className="text-sm">
                            {lessonIndex + 1}. {lesson.title}
                          </span>
                          {lesson.is_preview && (
                            <span className="text-xs bg-secondary px-2 py-1 rounded">
                              プレビュー
                            </span>
                          )}
                        </div>
                        <span className="text-sm text-muted-foreground">
                          {lesson.duration_minutes}分
                        </span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Reviews Section */}
          <div className="mt-12 space-y-4">
            <h2 className="text-2xl font-semibold">レビュー</h2>
            
            {/* Submit Review Form - only for enrolled users */}
            {isEnrolled && (
              <Card className="mb-6">
                <CardHeader>
                  <CardTitle>レビューを投稿</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">評価</label>
                    {renderStars(userReview.rating, true)}
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">コメント（任意）</label>
                    <textarea
                      className="w-full p-2 border rounded-md"
                      rows={3}
                      value={userReview.comment}
                      onChange={(e) => setUserReview({ ...userReview, comment: e.target.value })}
                      placeholder="このコースの感想を教えてください"
                    />
                  </div>
                  <Button
                    onClick={handleSubmitReview}
                    disabled={!userReview.rating || submittingReview}
                  >
                    {submittingReview ? '投稿中...' : 'レビューを投稿'}
                  </Button>
                </CardContent>
              </Card>
            )}

            {/* Reviews List */}
            {reviews.length === 0 ? (
              <p className="text-muted-foreground">まだレビューがありません</p>
            ) : (
              <div className="space-y-4">
                {reviews.map((review) => (
                  <Card key={review.id}>
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <div>
                          <CardTitle className="text-base">{review.user.full_name}</CardTitle>
                          <div className="flex items-center gap-2 mt-1">
                            {renderStars(review.rating)}
                            <span className="text-sm text-muted-foreground">
                              {new Date(review.created_at).toLocaleDateString('ja-JP')}
                            </span>
                          </div>
                        </div>
                      </div>
                    </CardHeader>
                    {review.comment && (
                      <CardContent>
                        <p className="text-sm">{review.comment}</p>
                      </CardContent>
                    )}
                  </Card>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="lg:col-span-1">
          <Card className="sticky top-20">
            <CardHeader>
              <CardTitle className="text-3xl">¥{course.price.toLocaleString()}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <Button 
                onClick={handleEnroll} 
                className="w-full" 
                size="lg"
                disabled={enrolling}
              >
                {enrolling ? '処理中...' : '今すぐ受講する'}
              </Button>
              
              <div className="space-y-2 pt-4">
                <h3 className="font-semibold mb-2">このコースに含まれるもの:</h3>
                <div className="flex items-center gap-2 text-sm">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span>{course.duration_hours}時間のオンデマンドビデオ</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span>{totalLessons}本のレッスン</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span>モバイルとPCからアクセス</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span>修了証明書</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}