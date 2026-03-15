import { createContext, useContext, useEffect, useState } from 'react'

const FontSizeContext = createContext({ fontSize: 18 })

export function useFontSize() {
  return useContext(FontSizeContext)
}

export function FontSizeProvider({ children }) {
  const [fontSize, setFontSize] = useState(() => {
    try {
      const profile = JSON.parse(localStorage.getItem('eduai_profile') || '{}')
      return profile.accessibility_settings?.font_size
        ? parseInt(profile.accessibility_settings.font_size, 10)
        : profile.font_size || 18
    } catch {
      return 18
    }
  })

  // Listen for profile changes (e.g. after CreateProfile saves)
  useEffect(() => {
    function onStorage(e) {
      if (e.key === 'eduai_profile') {
        try {
          const profile = JSON.parse(e.newValue || '{}')
          const size = profile.accessibility_settings?.font_size
            ? parseInt(profile.accessibility_settings.font_size, 10)
            : profile.font_size || 18
          setFontSize(size)
        } catch { /* ignore */ }
      }
    }
    window.addEventListener('storage', onStorage)
    return () => window.removeEventListener('storage', onStorage)
  }, [])

  // Apply CSS custom property to document root whenever fontSize changes
  useEffect(() => {
    document.documentElement.style.setProperty('--user-font-size', `${fontSize}px`)
  }, [fontSize])

  return (
    <FontSizeContext.Provider value={{ fontSize, setFontSize }}>
      {children}
    </FontSizeContext.Provider>
  )
}
