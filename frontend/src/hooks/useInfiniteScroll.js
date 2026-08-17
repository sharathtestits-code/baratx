import { useEffect, useRef, useState } from "react";
import { allowScrollPageLoad, isAutomatedBrowser } from "../antiScrapeClient";

/**
 * Calls `onLoadMore` when the sentinel element enters the viewport.
 * Skips while `disabled`, and refuses headless / rapid scroll scrapers.
 */
export function useInfiniteScroll({ disabled, onLoadMore, rootMargin = "240px" }) {
  const [node, setNode] = useState(null);
  const loadTimesRef = useRef([]);
  const blockedRef = useRef(isAutomatedBrowser());

  useEffect(() => {
    if (!node || disabled || blockedRef.current) return undefined;

    const observer = new IntersectionObserver(
      (entries) => {
        if (!entries.some((e) => e.isIntersecting)) return;
        if (blockedRef.current || isAutomatedBrowser()) {
          blockedRef.current = true;
          return;
        }
        if (!allowScrollPageLoad(loadTimesRef)) {
          // Burst scroll harvest — pause further auto-loads this session.
          blockedRef.current = true;
          return;
        }
        onLoadMore?.();
      },
      { root: null, rootMargin, threshold: 0 }
    );

    observer.observe(node);
    return () => observer.disconnect();
  }, [node, disabled, onLoadMore, rootMargin]);

  return setNode;
}
