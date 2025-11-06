import React from 'react'

/**
 * Format markdown-style content to React elements
 * Handles **bold** text and converts it to proper formatting
 */
export const formatMarkdownToReact = (text: string): React.ReactNode => {
  if (!text) return null
  
  // Split by ** to find bold sections
  const parts = text.split('**')
  
  return (
    <>
      {parts.map((part, index) => {
        // Odd indices are the text between ** markers (should be bold)
        if (index % 2 === 1) {
          return (
            <strong key={index} className="font-semibold text-gray-900">
              {part}
            </strong>
          )
        }
        return <span key={index}>{part}</span>
      })}
    </>
  )
}

/**
 * Strip markdown formatting and return plain text
 * Useful for previews and truncated content
 */
export const stripMarkdown = (text: string): string => {
  return text.replace(/\*\*/g, '')
}

/**
 * Format full content with paragraphs, lists, and sections
 */
export const formatContent = (content: string): React.ReactNode => {
  // Remove disclaimer text
  const cleanContent = content
    .replace(/\*\*Disclaimer\*\*:?\s*This is educational content.*?guidance\./gi, '')
    .replace(/This is educational content, not financial advice.*?guidance\./gi, '')
    .trim()
  
  // Split by double newlines to get paragraphs
  const paragraphs = cleanContent.split('\n\n')
  
  return (
    <div className="space-y-4">
      {paragraphs.map((para, index) => {
        // Check if paragraph starts with **Section Title**:
        const sectionMatch = para.match(/^\*\*(.*?)\*\*:?\s*(.*)$/s)
        
        if (sectionMatch) {
          const [, title, text] = sectionMatch
          const lines = text.split('\n').filter(line => line.trim())
          
          // Check if it's a bullet list (lines start with -)
          const isList = lines.length > 0 && lines.every(line => line.trim().startsWith('-'))
          
          return (
            <div key={index} className="mt-4">
              <h4 className="text-base font-semibold text-gray-900 mb-2">{title}</h4>
              {isList ? (
                <ul className="space-y-1.5 ml-4">
                  {lines.map((line, i) => (
                    <li key={i} className="flex items-start gap-2 text-gray-700 text-sm">
                      <span className="text-primary-600 mt-0.5">•</span>
                      <span>{formatMarkdownToReact(line.replace(/^-\s*/, ''))}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-gray-700 text-sm leading-relaxed whitespace-pre-line">
                  {formatMarkdownToReact(text)}
                </p>
              )}
            </div>
          )
        }
        
        // Regular paragraph - check for inline bold markers
        return (
          <p key={index} className="text-gray-700 text-sm leading-relaxed">
            {formatMarkdownToReact(para)}
          </p>
        )
      })}
    </div>
  )
}

