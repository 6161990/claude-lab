/**
 * API 에러 클래스
 * HTTP 에러 및 네트워크 에러를 처리
 */
export class ApiError extends Error {
  constructor(
    public status: number,
    public statusText: string,
    message?: string
  ) {
    super(message || `API Error: ${status} ${statusText}`)
    this.name = "ApiError"
  }
}

/**
 * API 요청 옵션 타입
 */
interface RequestOptions extends RequestInit {
  timeout?: number
}

/**
 * API 클라이언트 클래스
 * fetch API를 래핑하여 타입 안전성과 에러 핸들링 제공
 */
class ApiClient {
  private baseURL: string
  private defaultTimeout: number = 10000 // 10초

  constructor(baseURL: string = "") {
    this.baseURL = baseURL
  }

  /**
   * fetch 요청을 수행하는 내부 메서드
   */
  private async request<T>(
    endpoint: string,
    options: RequestOptions = {}
  ): Promise<T> {
    const { timeout = this.defaultTimeout, ...fetchOptions } = options

    const url = `${this.baseURL}${endpoint}`

    // 타임아웃 처리를 위한 AbortController
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), timeout)

    try {
      const response = await fetch(url, {
        ...fetchOptions,
        signal: controller.signal,
      })

      clearTimeout(timeoutId)

      // HTTP 에러 처리
      if (!response.ok) {
        throw new ApiError(response.status, response.statusText)
      }

      // JSON 파싱
      const data = await response.json()
      return data as T
    } catch (error) {
      clearTimeout(timeoutId)

      // AbortController로 인한 타임아웃 에러 처리
      if (error instanceof Error && error.name === "AbortError") {
        throw new Error("요청 시간이 초과되었습니다")
      }

      // ApiError는 그대로 전달
      if (error instanceof ApiError) {
        throw error
      }

      // 기타 네트워크 에러
      throw new Error("네트워크 오류가 발생했습니다")
    }
  }

  /**
   * GET 요청
   */
  async get<T>(endpoint: string, options?: RequestOptions): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: "GET",
    })
  }

  /**
   * POST 요청
   */
  async post<T>(
    endpoint: string,
    body?: unknown,
    options?: RequestOptions
  ): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
      body: JSON.stringify(body),
    })
  }

  /**
   * PUT 요청
   */
  async put<T>(
    endpoint: string,
    body?: unknown,
    options?: RequestOptions
  ): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
      body: JSON.stringify(body),
    })
  }

  /**
   * DELETE 요청
   */
  async delete<T>(endpoint: string, options?: RequestOptions): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: "DELETE",
    })
  }

  /**
   * multipart/form-data 업로드
   * Content-Type 헤더를 명시하지 않음 - 브라우저가 boundary 포함하여 자동 설정
   */
  async uploadForm<T>(endpoint: string, formData: FormData, options?: RequestOptions): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: "POST",
      body: formData,
    })
  }
}

// 기본 API 클라이언트 인스턴스 생성 및 export
export const apiClient = new ApiClient(process.env.NEXT_PUBLIC_API_URL || "")
