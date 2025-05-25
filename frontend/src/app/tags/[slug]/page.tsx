'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import { api } from '@/lib/api'
import { CourseCard } from '@/components/course-card'

export default function TagPage() {
  const params = useParams()
  const [courses, setCourses] = useState<any[]>([])
  const [tag, setTag] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (params.slug) {
      loadTagCourses(params.slug as string)
    }
  }, [params.slug])

  async function loadTagCourses(slug: string) {
    setLoading(true)
    try {
      // Get tag info
      const tags = await api.getTags()
      const currentTag = tags.find((t: any) => t.slug === slug)
      setTag(currentTag)
      
      // Get courses for this tag
      const data = await api.getCoursesByTag(slug)
      setCourses(data)
    } catch (e) {
      setError('タグのコース取得に失敗しました')
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <main className="p-6 space-y-4">
        <p className="text-center">読み込み中...</p>
      </main>
    )
  }

  if (error || !tag) {
    return (
      <main className="p-6 space-y-4">
        <p className="text-center text-red-500">{error || 'タグが見つかりません'}</p>
      </main>
    )
  }

  return (
    <main className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold">{tag.name}</h1>
        <p className="text-muted-foreground mt-2">{courses.length}件のコース</p>
      </div>
      
      {courses.length === 0 ? (
        <p className="text-center text-muted-foreground">このタグのコースはまだありません</p>
      ) : (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {courses.map((c, index) => (
            <CourseCard key={c.id} course={c} index={index} />
          ))}
        </div>
      )}
    </main>
  )
}