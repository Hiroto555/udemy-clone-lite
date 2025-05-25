'use client'

import { useEffect, useState } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import { api } from '@/lib/api'
import { CourseCard } from '../../components/course-card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'

export default function CoursesPage() {
  const [courses, setCourses] = useState<any[]>([])
  const [tags, setTags] = useState<any[]>([])
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  
  const searchParams = useSearchParams()
  const router = useRouter()
  
  // Form state
  const [searchQuery, setSearchQuery] = useState(searchParams.get('q') || '')
  const [selectedTag, setSelectedTag] = useState(searchParams.get('tag') || '')
  const [priceMin, setPriceMin] = useState(searchParams.get('price_min') || '')
  const [priceMax, setPriceMax] = useState(searchParams.get('price_max') || '')

  useEffect(() => {
    loadTags()
  }, [])

  useEffect(() => {
    loadCourses()
  }, [searchParams])

  async function loadTags() {
    try {
      const data = await api.getTags()
      setTags(data)
    } catch (e) {
      console.error(e)
    }
  }

  async function loadCourses() {
    setLoading(true)
    try {
      const params: any = {}
      const q = searchParams.get('q')
      const tag = searchParams.get('tag')
      const price_min = searchParams.get('price_min')
      const price_max = searchParams.get('price_max')
      
      if (q) params.q = q
      if (tag) params.tag = tag
      if (price_min) params.price_min = Number(price_min)
      if (price_max) params.price_max = Number(price_max)
      
      const data = await api.getCourses(params)
      setCourses(data)
    } catch (e) {
      setError('コース取得に失敗しました')
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  function handleSearch(e: React.FormEvent) {
    e.preventDefault()
    const params = new URLSearchParams()
    if (searchQuery) params.set('q', searchQuery)
    if (selectedTag) params.set('tag', selectedTag)
    if (priceMin) params.set('price_min', priceMin)
    if (priceMax) params.set('price_max', priceMax)
    
    router.push(`/courses?${params.toString()}`)
  }

  function handleClearFilters() {
    setSearchQuery('')
    setSelectedTag('')
    setPriceMin('')
    setPriceMax('')
    router.push('/courses')
  }

  if (error) return <p className="p-6 text-red-500">{error}</p>

  return (
    <main className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">公開コース一覧</h1>
      
      {/* Search and Filter Form */}
      <form onSubmit={handleSearch} className="space-y-4 p-6 bg-card rounded-lg border">
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {/* Search Input */}
          <div className="space-y-2">
            <Label htmlFor="search">検索キーワード</Label>
            <Input
              id="search"
              type="text"
              placeholder="タイトルや説明で検索"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          
          {/* Tag Dropdown */}
          <div className="space-y-2">
            <Label htmlFor="tag">タグ</Label>
            <select
              id="tag"
              value={selectedTag}
              onChange={(e) => setSelectedTag(e.target.value)}
              className="w-full h-10 px-3 py-2 text-sm bg-background border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring"
            >
              <option value="">すべてのタグ</option>
              {tags.map((tag) => (
                <option key={tag.id} value={tag.slug}>
                  {tag.name}
                </option>
              ))}
            </select>
          </div>
          
          {/* Price Range */}
          <div className="space-y-2">
            <Label htmlFor="price_min">最低価格</Label>
            <Input
              id="price_min"
              type="number"
              placeholder="0"
              min="0"
              value={priceMin}
              onChange={(e) => setPriceMin(e.target.value)}
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="price_max">最高価格</Label>
            <Input
              id="price_max"
              type="number"
              placeholder="999999"
              min="0"
              value={priceMax}
              onChange={(e) => setPriceMax(e.target.value)}
            />
          </div>
        </div>
        
        <div className="flex gap-2">
          <Button type="submit">検索</Button>
          <Button type="button" variant="outline" onClick={handleClearFilters}>
            フィルターをクリア
          </Button>
        </div>
      </form>
      
      {/* Results */}
      {loading ? (
        <p className="text-center">読み込み中...</p>
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
