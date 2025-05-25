'use client'
import Link from 'next/link'
import { Card, CardContent, CardFooter, CardHeader } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { motion } from 'framer-motion'
import { Star } from 'lucide-react'

export function CourseCard({ course, index = 0 }: { course: any; index?: number }) {
  const renderStars = (rating: number) => {
    return (
      <div className="flex gap-0.5">
        {[1, 2, 3, 4, 5].map((star) => (
          <Star
            key={star}
            className={`h-3 w-3 ${
              star <= rating ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'
            }`}
          />
        ))}
      </div>
    )
  }
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.1 }}
    >
      <Link href={`/courses/${course.id}`} className="block">
        <Card className="h-full transition-all duration-300 hover:shadow-lg hover:-translate-y-1">
        <div className="relative aspect-video">
          <img 
            src={`https://picsum.photos/seed/${course.id}/400/225`}
            alt={course.title}
            className="w-full h-full object-cover rounded-t-lg"
          />
          <Badge 
            variant="secondary" 
            className="absolute top-2 right-2"
          >
            ${course.price?.toFixed(2) || '0.00'}
          </Badge>
        </div>
        <CardHeader className="pb-2">
          <h3 className="font-semibold line-clamp-2">{course.title}</h3>
        </CardHeader>
        <CardContent className="space-y-2">
          <p className="text-sm text-muted-foreground line-clamp-3">{course.description}</p>
          {course.average_rating && (
            <div className="flex items-center gap-2">
              {renderStars(Math.round(course.average_rating))}
              <span className="text-xs text-muted-foreground">
                {course.average_rating.toFixed(1)}
              </span>
            </div>
          )}
          {course.tags && course.tags.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {course.tags.slice(0, 2).map((tag: any) => (
                <Badge key={tag.id} variant="secondary" className="text-xs">
                  {tag.name}
                </Badge>
              ))}
              {course.tags.length > 2 && (
                <Badge variant="secondary" className="text-xs">
                  +{course.tags.length - 2}
                </Badge>
              )}
            </div>
          )}
        </CardContent>
        <CardFooter className="pt-0">
          <p className="text-sm text-muted-foreground">
            {(course.enrolled_count || 0).toLocaleString()}人が受講中
          </p>
        </CardFooter>
      </Card>
    </Link>
    </motion.div>
  )
}
