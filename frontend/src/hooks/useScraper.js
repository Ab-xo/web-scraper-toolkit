import { useState, useCallback } from 'react'
import { scrapeUrl, queryContent } from '../api/client'

export function useScraper() {
  const [status,  setStatus]  = useState('idle')
  const [result,  setResult]  = useState(null)
  const [error,   setError]   = useState(null)
  const [history, setHistory] = useState([])

  const scrape = useCallback(async (url, usePlaywright = false) => {
    setStatus('loading')
    setError(null)

    try {
      const { data } = await scrapeUrl(url, usePlaywright)
      setResult(data)
      setStatus('success')

      // add to history, remove duplicate if same url was scraped before
      setHistory((prev) => {
        const deduped = prev.filter((h) => h.url !== url)
        const entry = {
          url,
          title: data.title ?? url,
          timestamp: new Date().toISOString(),
        }
        return [entry, ...deduped].slice(0, 10)
      })

    } catch (err) {
      setError(err.message)
      setStatus('error')
    }
  }, [])

  // query has its own loading state inside QueryPanel, not here
  const query = useCallback(async (html, intent, baseUrl = null) => {
    const { data } = await queryContent(html, intent, baseUrl)
    return data
  }, [])

  const reset = useCallback(() => {
    setStatus('idle')
    setResult(null)
    setError(null)
  }, [])

  return { status, result, error, history, scrape, query, reset }
}