'use client'

import Link from 'next/link'
import { useEffect, useState } from 'react'
import { useAuth } from '@/contexts/auth'
import { Button } from '@/components/ui/button'
import { BookOpen, LogOut, User, ChevronDown } from 'lucide-react'
import { ThemeToggle } from '@/components/theme-toggle'
import { api } from '@/lib/api'

export function Header() {
  const { user, logout } = useAuth()
  const [tags, setTags] = useState<any[]>([])
  const [tagsOpen, setTagsOpen] = useState(false)

  useEffect(() => {
    loadTags()
  }, [])

  async function loadTags() {
    try {
      const data = await api.getTags()
      setTags(data)
    } catch (e) {
      console.error('Failed to load tags:', e)
    }
  }

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 items-center">
        <div className="mr-4 flex">
          <Link href="/" className="mr-6 flex items-center space-x-2">
            <BookOpen className="h-6 w-6" />
            <span className="font-bold">講座サイト</span>
          </Link>
          <nav className="flex items-center space-x-6 text-sm font-medium">
            <Link
              href="/courses"
              className="transition-colors hover:text-foreground/80 text-foreground"
            >
              コース一覧
            </Link>
            <div className="relative">
              <button
                onClick={() => setTagsOpen(!tagsOpen)}
                className="flex items-center gap-1 transition-colors hover:text-foreground/80 text-foreground"
              >
                タグ
                <ChevronDown className="h-4 w-4" />
              </button>
              {tagsOpen && (
                <div className="absolute top-full left-0 mt-2 w-48 bg-popover border rounded-md shadow-md p-2 z-50">
                  {tags.length === 0 ? (
                    <p className="text-sm text-muted-foreground p-2">タグがありません</p>
                  ) : (
                    tags.map((tag) => (
                      <Link
                        key={tag.id}
                        href={`/tags/${tag.slug}`}
                        className="block px-3 py-2 text-sm hover:bg-accent rounded-sm"
                        onClick={() => setTagsOpen(false)}
                      >
                        {tag.name}
                      </Link>
                    ))
                  )}
                </div>
              )}
            </div>
          </nav>
        </div>
        <div className="flex flex-1 items-center justify-end space-x-2">
          {user ? (
            <>
              <Link href="/dashboard">
                <Button variant="ghost" size="sm">
                  <User className="mr-2 h-4 w-4" />
                  ダッシュボード
                </Button>
              </Link>
              <Button variant="ghost" size="sm" onClick={logout}>
                <LogOut className="mr-2 h-4 w-4" />
                ログアウト
              </Button>
            </>
          ) : (
            <>
              <Link href="/login">
                <Button variant="ghost" size="sm">
                  ログイン
                </Button>
              </Link>
              <Link href="/register">
                <Button size="sm">
                  新規登録
                </Button>
              </Link>
            </>
          )}
          <ThemeToggle />
        </div>
      </div>
    </header>
  )
}