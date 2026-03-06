"use client"

import { useEffect, useState } from "react"

/**
 * 미디어 쿼리 상태를 추적하는 커스텀 훅
 * SSR 안전성을 보장하며 브레이크포인트 감지에 사용
 *
 * @param query - CSS 미디어 쿼리 문자열 (예: "(min-width: 768px)")
 * @returns 미디어 쿼리가 매치되면 true, 아니면 false
 *
 * @example
 * const isMobile = useMediaQuery("(max-width: 768px)")
 * const isDesktop = useMediaQuery("(min-width: 1024px)")
 */
export function useMediaQuery(query: string) {
  const [matches, setMatches] = useState(false)

  useEffect(() => {
    const media = window.matchMedia(query)

    // 변경 리스너 등록
    const listener = (event: MediaQueryListEvent) => {
      setMatches(event.matches)
    }

    // 초기 상태 설정 (리스너로 처리)
    setMatches(media.matches)

    // 구형 브라우저 호환성
    if (media.addEventListener) {
      media.addEventListener("change", listener)
    } else {
      media.addListener(listener)
    }

    // 클린업
    return () => {
      if (media.removeEventListener) {
        media.removeEventListener("change", listener)
      } else {
        media.removeListener(listener)
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [query])

  return matches
}
