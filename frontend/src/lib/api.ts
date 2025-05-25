import Cookies from 'js-cookie'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

interface ApiError {
  detail: string
}

class ApiClient {
  private async getAccessToken(): Promise<string | undefined> {
    return Cookies.get('access_token')
  }

  private async getRefreshToken(): Promise<string | undefined> {
    return Cookies.get('refresh_token')
  }

  private setTokens(tokens: TokenResponse) {
    Cookies.set('access_token', tokens.access_token, {
      expires: 1 / 96, // 15 minutes
      sameSite: 'lax',
      secure: process.env.NODE_ENV === 'production'
    })
    Cookies.set('refresh_token', tokens.refresh_token, {
      expires: 7, // 7 days
      sameSite: 'lax',
      secure: process.env.NODE_ENV === 'production'
    })
  }

  private clearTokens() {
    Cookies.remove('access_token')
    Cookies.remove('refresh_token')
  }

  private async refreshAccessToken(): Promise<boolean> {
    const refreshToken = await this.getRefreshToken()
    if (!refreshToken) return false

    try {
      const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh_token: refreshToken }),
      })

      if (!response.ok) {
        this.clearTokens()
        return false
      }

      const tokens: TokenResponse = await response.json()
      this.setTokens(tokens)
      return true
    } catch (error) {
      this.clearTokens()
      return false
    }
  }

  async request<T = any>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const accessToken = await this.getAccessToken()
    
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    }

    if (accessToken) {
      headers['Authorization'] = `Bearer ${accessToken}`
    }

    let response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    })

    // If 401, try to refresh token
    if (response.status === 401 && accessToken) {
      const refreshed = await this.refreshAccessToken()
      if (refreshed) {
        const newAccessToken = await this.getAccessToken()
        headers['Authorization'] = `Bearer ${newAccessToken}`
        response = await fetch(`${API_BASE_URL}${endpoint}`, {
          ...options,
          headers,
        })
      }
    }

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || 'API request failed')
    }

    return response.json()
  }

  // Auth endpoints
  async login(email: string, password: string): Promise<TokenResponse> {
    const formData = new FormData()
    formData.append('username', email)
    formData.append('password', password)

    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || 'Login failed')
    }

    const tokens: TokenResponse = await response.json()
    this.setTokens(tokens)
    return tokens
  }

  async register(email: string, password: string, name: string): Promise<any> {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, full_name: name }),
    })
  }

  async logout() {
    this.clearTokens()
  }

  // Course endpoints
  async getCourses(params?: {
    q?: string
    tag?: string
    price_min?: number
    price_max?: number
    skip?: number
    limit?: number
  }) {
    const searchParams = new URLSearchParams()
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          searchParams.append(key, value.toString())
        }
      })
    }
    const query = searchParams.toString()
    return this.request(`/courses${query ? `?${query}` : ''}`)
  }

  async getCourse(id: string) {
    return this.request(`/courses/${id}`)
  }

  async getEnrolledCourses() {
    return this.request('/users/me/enrollments')
  }

  // User endpoints
  async getCurrentUser() {
    return this.request('/users/me')
  }

  // Tag endpoints
  async getTags() {
    return this.request('/tags')
  }

  async getCoursesByTag(slug: string) {
    return this.request(`/tags/${slug}/courses`)
  }

  // Review endpoints
  async getReviews(courseId: string) {
    return this.request(`/courses/${courseId}/reviews`)
  }

  async createReview(courseId: string, rating: number, comment?: string) {
    return this.request(`/courses/${courseId}/reviews`, {
      method: 'POST',
      body: JSON.stringify({ rating, comment }),
    })
  }
}

export const api = new ApiClient()
export default api