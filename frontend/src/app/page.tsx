'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import api from '@/lib/api'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Clock, Users } from 'lucide-react'

interface Course {
  id: string
  title: string
  description: string
  instructor_name: string
  price: number
  duration_hours: number
  level: string
  enrolled_count: number
}

export default function Home() {
  const [courses, setCourses] = useState<Course[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadCourses()
  }, [])

  const loadCourses = async () => {
    try {
      const data = await api.getCourses()
      setCourses(data)
    } catch (err) {
      setError('コースの読み込みに失敗しました')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">読み込み中...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center text-red-500">{error}</div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-4">人気のコース</h1>
        <p className="text-lg text-muted-foreground">
          あなたのスキルアップに最適なコースを見つけましょう
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {courses.map((course) => (
          <Card key={course.id} className="flex flex-col">
            <CardHeader>
              <CardTitle>{course.title}</CardTitle>
              <CardDescription>講師: {course.instructor_name}</CardDescription>
            </CardHeader>
            <CardContent className="flex-grow">
              <p className="text-sm text-muted-foreground mb-4">
                {course.description}
              </p>
              <div className="flex items-center gap-4 text-sm">
                <div className="flex items-center gap-1">
                  <Clock className="h-4 w-4" />
                  <span>{course.duration_hours}時間</span>
                </div>
                <div className="flex items-center gap-1">
                  <Users className="h-4 w-4" />
                  <span>{course.enrolled_count}人</span>
                </div>
              </div>
              <div className="mt-2">
                <span className="inline-block px-2 py-1 text-xs rounded-full bg-secondary">
                  {course.level}
                </span>
              </div>
            </CardContent>
            <CardFooter className="flex justify-between items-center">
              <span className="text-2xl font-bold">¥{course.price.toLocaleString()}</span>
              <Link href={`/courses/${course.id}`}>
                <Button>詳細を見る</Button>
              </Link>
            </CardFooter>
          </Card>
        ))}
      </div>
    </div>
  )
}