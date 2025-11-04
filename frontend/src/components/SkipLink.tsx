import React from 'react'

interface SkipLinkProps {
  href: string
  label?: string
}

export const SkipLink: React.FC<SkipLinkProps> = ({
  href,
  label = 'Skip to main content',
}) => {
  return (
    <a
      href={href}
      className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-primary-600 focus:text-white focus:rounded-lg focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 focus:outline-none"
      aria-label={label}
    >
      {label}
    </a>
  )
}

export default SkipLink


