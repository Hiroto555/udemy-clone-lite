'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/auth'
import api from '@/lib/api'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { BookOpen, Clock, BarChart, Play } from 'lucide-react'

interface EnrolledCourse {
  id: string
  course_id: string
  course_title: string
  instructor_name: string
  progress_percentage: number
  last_accessed: string | null
  enrolled_at: string
}

export default function DashboardPage() {
  const router = useRouter()
  const { user, loading: authLoading } = useAuth()
  const [enrolledCourses, setEnrolledCourses] = useState<EnrolledCourse[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login')
    } else if (user) {
      loadEnrolledCourses()
    }
  }, [user, authLoading, router])

  const loadEnrolledCourses = async () => {
    try {
      const data = await api.getEnrolledCourses()
      setEnrolledCourses(data)
    } catch (err) {
      setError('受講中のコースの読み込みに失敗しました')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  if (authLoading || loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">読み込み中...</div>
      </div>
    )
  }

  if (!user) {
    return null
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">ダッシュボード</h1>
        <p className="text-lg text-muted-foreground">
          ようこそ、{user.full_name}さん！
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              受講中のコース
            </CardTitle>
            <BookOpen className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{enrolledCourses.length}</div>
            <p className="text-xs text-muted-foreground">
              現在受講中
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              学習時間
            </CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">0時間</div>
            <p className="text-xs text-muted-foreground">
              今月の学習時間
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              平均進捗率
            </CardTitle>
            <BarChart className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {enrolledCourses.length > 0
                ? Math.round(
                    enrolledCourses.reduce((acc, course) => acc + course.progress_percentage, 0) /
                    enrolledCourses.length
                  )
                : 0}%
            </div>
            <p className="text-xs text-muted-foreground">
              全コースの平均
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="space-y-4">
        <h2 className="text-2xl font-semibold mb-4">受講中のコース</h2>
        
        {error && (
          <div className="text-center text-red-500 py-4">{error}</div>
        )}

        {enrolledCourses.length === 0 ? (
          <Card>
            <CardContent className="text-center py-12">
              <BookOpen className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
              <p className="text-lg mb-4">まだコースを受講していません</p>
              <Link href="/">
                <Button>コースを探す</Button>
              </Link>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {enrolledCourses.map((enrollment) => (
              <Card key={enrollment.id} className="flex flex-col">
                <CardHeader>
                  <CardTitle className="line-clamp-2">{enrollment.course_title}</CardTitle>
                  <CardDescription>講師: {enrollment.instructor_name}</CardDescription>
                </CardHeader>
                <CardContent className="flex-grow">
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>進捗率</span>
                      <span className="font-semibold">{enrollment.progress_percentage}%</span>
                    </div>
                    <div className="w-full bg-secondary rounded-full h-2">
                      <div
                        className="bg-primary h-2 rounded-full transition-all"
                        style={{ width: `${enrollment.progress_percentage}%` }}
                      />
                    </div>
                  </div>
                  {enrollment.last_accessed && (
                    <p className="text-sm text-muted-foreground mt-4">
                      最終アクセス: {new Date(enrollment.last_accessed).toLocaleDateString('ja-JP')}
                    </p>
                  )}
                </CardContent>
                <CardFooter>
                  <Link href={`/courses/${enrollment.course_id}/learn`} className="w-full">
                    <Button className="w-full" variant="default">
                      <Play className="mr-2 h-4 w-4" />
                      学習を続ける
                    </Button>
                  </Link>
                </CardFooter>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}