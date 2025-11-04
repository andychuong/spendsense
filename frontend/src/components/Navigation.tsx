import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/store'
import { FaBars, FaTimes, FaHome, FaUser, FaLightbulb, FaCog, FaUpload, FaSignOutAlt } from 'react-icons/fa'

const Navigation = () => {
  const location = useLocation()
  const navigate = useNavigate()
  const { isAuthenticated, user, logout } = useAuthStore()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const handleLogout = () => {
    logout()
    navigate('/login')
    setMobileMenuOpen(false)
  }

  const navigationItems = [
    { path: '/', label: 'Dashboard', icon: FaHome },
    { path: '/profile', label: 'Profile', icon: FaUser },
    { path: '/recommendations', label: 'Recommendations', icon: FaLightbulb },
    { path: '/upload', label: 'Upload', icon: FaUpload },
    { path: '/settings', label: 'Settings', icon: FaCog },
  ]

  if (!isAuthenticated) {
    return null
  }

  const isActive = (path: string) => location.pathname === path

  return (
    <>
      {/* Mobile Menu Overlay */}
      {mobileMenuOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={() => setMobileMenuOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* Mobile Navigation */}
      <nav className="lg:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 z-50" aria-label="Main navigation">
        <div className="flex items-center justify-around px-2 py-2">
          {navigationItems.slice(0, 4).map((item) => {
            const Icon = item.icon
            return (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => setMobileMenuOpen(false)}
                className={`
                  flex flex-col items-center justify-center p-2 rounded-lg transition-colors duration-200
                  min-w-[60px] min-h-[60px] touch-manipulation focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500
                  ${isActive(item.path)
                    ? 'text-primary-600 bg-primary-50'
                    : 'text-gray-600 hover:text-primary-600 hover:bg-gray-50'
                  }
                `}
                aria-label={item.label}
                aria-current={isActive(item.path) ? 'page' : undefined}
              >
                <Icon className="h-6 w-6 mb-1" aria-hidden="true" />
                <span className="text-xs font-medium">{item.label}</span>
              </Link>
            )
          })}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="flex flex-col items-center justify-center p-2 rounded-lg transition-colors duration-200 min-w-[60px] min-h-[60px] touch-manipulation text-gray-600 hover:text-primary-600 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            aria-label="More menu"
            aria-expanded={mobileMenuOpen}
            aria-controls="mobile-menu-panel"
          >
            {mobileMenuOpen ? (
              <>
                <FaTimes className="h-6 w-6 mb-1" aria-hidden="true" />
                <span className="text-xs font-medium">Close</span>
              </>
            ) : (
              <>
                <FaBars className="h-6 w-6 mb-1" aria-hidden="true" />
                <span className="text-xs font-medium">More</span>
              </>
            )}
          </button>
        </div>

        {/* Mobile Menu Panel */}
        {mobileMenuOpen && (
          <div id="mobile-menu-panel" className="absolute bottom-full left-0 right-0 bg-white border-t border-gray-200 shadow-lg" role="menu">
            <div className="px-4 py-3 space-y-1">
              {navigationItems.slice(4).map((item) => {
                const Icon = item.icon
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    onClick={() => setMobileMenuOpen(false)}
                    className={`
                      flex items-center gap-3 px-4 py-3 rounded-lg transition-colors duration-200
                      touch-manipulation min-h-[44px] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500
                      ${isActive(item.path)
                        ? 'bg-primary-50 text-primary-600'
                        : 'text-gray-700 hover:bg-gray-50'
                      }
                    `}
                    role="menuitem"
                    aria-current={isActive(item.path) ? 'page' : undefined}
                  >
                    <Icon className="h-5 w-5" aria-hidden="true" />
                    <span className="font-medium">{item.label}</span>
                  </Link>
                )
              })}
              <button
                onClick={handleLogout}
                className="flex items-center gap-3 px-4 py-3 rounded-lg transition-colors duration-200 text-red-600 hover:bg-red-50 w-full touch-manipulation min-h-[44px] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                role="menuitem"
              >
                <FaSignOutAlt className="h-5 w-5" aria-hidden="true" />
                <span className="font-medium">Logout</span>
              </button>
              {user?.email && (
                <div className="px-4 py-2 text-xs text-gray-500 border-t border-gray-200 mt-2 pt-2">
                  {user.email}
                </div>
              )}
            </div>
          </div>
        )}
      </nav>

      {/* Desktop Navigation */}
      <nav className="hidden lg:block bg-white border-b border-gray-200 sticky top-0 z-50" aria-label="Main navigation">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-8">
              <Link to="/" className="text-xl font-bold text-primary-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500" aria-label="SpendSense Home">
                SpendSense
              </Link>
              <div className="flex items-center gap-1" role="list">
                {navigationItems.map((item) => {
                  const Icon = item.icon
                  return (
                    <Link
                      key={item.path}
                      to={item.path}
                      className={`
                        flex items-center gap-2 px-4 py-2 rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500
                        ${isActive(item.path)
                          ? 'bg-primary-50 text-primary-600'
                          : 'text-gray-600 hover:text-primary-600 hover:bg-gray-50'
                        }
                      `}
                      aria-current={isActive(item.path) ? 'page' : undefined}
                      role="listitem"
                    >
                      <Icon className="h-4 w-4" aria-hidden="true" />
                      <span className="font-medium">{item.label}</span>
                    </Link>
                  )
                })}
              </div>
            </div>
            <div className="flex items-center gap-4">
              {user?.email && (
                <span className="text-sm text-gray-600" aria-label={`Logged in as ${user.email}`}>
                  {user.email}
                </span>
              )}
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 px-4 py-2 rounded-lg transition-colors duration-200 text-gray-600 hover:text-red-600 hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                aria-label="Logout"
              >
                <FaSignOutAlt className="h-4 w-4" aria-hidden="true" />
                <span className="font-medium">Logout</span>
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Bottom padding for mobile nav */}
      <div className="lg:hidden h-20" />
    </>
  )
}

export default Navigation

