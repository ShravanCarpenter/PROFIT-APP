// src/components/Navbar.js
import React, { useState, useEffect, useRef } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export const Navbar = () => {
    const { user, isAuthenticated, logout } = useAuth();
    const location = useLocation();
    const navigate = useNavigate();
    const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
    const menuRef = useRef(null);

    const handleLogout = async () => {
        try {
            await logout(); // Make sure logout completes
            setIsUserMenuOpen(false);
            navigate('/login', { replace: true }); // Use replace to avoid back button issues
        } catch (error) {
            console.error('Logout error:', error);
            // Force navigation even if logout fails
            setIsUserMenuOpen(false);
            navigate('/login', { replace: true });
        }
    };

    const handleProfileClick = () => {
        setIsUserMenuOpen(false);
        navigate('/profile');
    };

    // Close menu when clicking outside
    useEffect(() => {
        const handleClickOutside = (event) => {
            if (menuRef.current && !menuRef.current.contains(event.target)) {
                setIsUserMenuOpen(false);
            }
        };

        if (isUserMenuOpen) {
            document.addEventListener('mousedown', handleClickOutside);
        }

        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, [isUserMenuOpen]);

    // Close menu on route change
    useEffect(() => {
        setIsUserMenuOpen(false);
    }, [location.pathname]);

    // Get user initials for avatar
    const getUserInitials = (user) => {
        if (user?.username) {
            return user.username.substring(0, 2).toUpperCase();
        } else if (user?.email) {
            return user.email.substring(0, 2).toUpperCase();
        }
        return 'U';
    };

    // Get display name
    const getDisplayName = (user) => {
        return user?.username || user?.email || 'User';
    };

    return (
        <nav className="bg-white shadow-md sticky top-0 z-50">
            <div className="container mx-auto px-4 lg:px-6">
                <div className="flex justify-between items-center h-16">
                    {/* Logo */}
                    <Link to="/" className="flex items-center space-x-2 flex-shrink-0">
                        <div className="h-8 w-8 bg-indigo-600 rounded-lg flex items-center justify-center">
                            <span className="text-white font-bold text-lg">PF</span>
                        </div>
                        <span className="text-xl font-bold text-indigo-800 hidden sm:block">PROFit</span>
                    </Link>

                    {/* Navigation Links */}
                    <div className="flex items-center space-x-2 sm:space-x-3 lg:space-x-4 flex-1 justify-center mr-20">
                        <NavButton to="/" current={location.pathname === "/"}>
                            <span className="flex items-center space-x-1">
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" d="M3 12l9-9 9 9M4 10v10a1 1 0 001 1h3m10-11v10a1 1 0 01-1 1h-3m-6 0h6" />
                                </svg>
                                <span className="hidden sm:inline">Home</span>
                            </span>
                        </NavButton>

                        {isAuthenticated() ? (
                            <>
                                <NavButton to="/live" current={location.pathname === "/live"}>
                                    <span className="flex items-center space-x-1">
                                        <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                                            <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" fill="none" />
                                            <circle cx="12" cy="12" r="4" fill="currentColor" />
                                        </svg>
                                        <span className="hidden sm:inline">Live</span>
                                    </span>
                                </NavButton>
                                <NavButton to="/upload" current={location.pathname === "/upload"}>
                                    <span className="flex items-center space-x-1">
                                        <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2M7 10l5-5 5 5M12 15V3" />
                                        </svg>
                                        <span className="hidden sm:inline">Upload</span>
                                    </span>
                                </NavButton>
                            </>
                        ) : (
                            <>
                                <NavButton to="/login" current={location.pathname === "/login"}>
                                    <span className="flex items-center space-x-1">
                                        <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" d="M5.121 17.804A13.937 13.937 0 0112 15c2.485 0 4.797.755 6.879 2.047M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                                        </svg>
                                        <span className="hidden sm:inline">Login</span>
                                    </span>
                                </NavButton>
                                <NavButton to="/register" current={location.pathname === "/register"}>
                                    <span className="flex items-center space-x-1">
                                        <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" d="M16 21v-2a4 4 0 00-8 0v2M12 11a4 4 0 100-8 4 4 0 000 8z" />
                                            <path strokeLinecap="round" strokeLinejoin="round" d="M20 8v6M23 11h-6" />
                                        </svg>
                                        <span className="hidden sm:inline">Register</span>
                                    </span>
                                </NavButton>
                            </>
                        )}
                    </div>

                    {/* User Menu (only show when authenticated) */}
                    {isAuthenticated() && (
                        <div className="relative flex-shrink-0" ref={menuRef}>
                            <button
                                onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
                                className="flex items-center space-x-2 py-2 px-3 rounded-lg font-medium transition-all duration-200 text-gray-600 hover:text-indigo-600 hover:bg-indigo-50 border border-transparent hover:border-indigo-200 cursor-pointer focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                aria-expanded={isUserMenuOpen}
                                aria-haspopup="true"
                            >
                                {/* User Avatar Circle */}
                                <div className="h-8 w-8 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center shadow-sm">
                                    <span className="text-white font-semibold text-sm">
                                        {getUserInitials(user)}
                                    </span>
                                </div>
                                {/* User name */}
                                <span className="text-sm hidden sm:inline max-w-32 truncate">
                                    {getDisplayName(user)}
                                </span>
                                {/* Dropdown arrow */}
                                <svg 
                                    className={`w-4 h-4 transition-transform duration-200 ${
                                        isUserMenuOpen ? 'rotate-180' : ''
                                    }`} 
                                    fill="none" 
                                    stroke="currentColor" 
                                    strokeWidth="2" 
                                    viewBox="0 0 24 24"
                                >
                                    <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
                                </svg>
                            </button>
                            
                            {isUserMenuOpen && (
                                <div className="absolute right-0 mt-2 bg-white rounded-lg shadow-lg border border-gray-200 py-2 min-w-56 max-w-80 z-50">
                                    <div className="px-4 py-3 border-b border-gray-100">
                                        <div className="flex items-center space-x-3">
                                            <div className="h-10 w-10 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center shadow-sm">
                                                <span className="text-white font-semibold text-base">
                                                    {getUserInitials(user)}
                                                </span>
                                            </div>
                                            <div className="flex-1 min-w-0">
                                                <p className="font-medium text-gray-900 text-sm truncate">
                                                    {user?.username || 'User'}
                                                </p>
                                                {user?.email && (
                                                    <p className="text-xs text-gray-500 truncate">
                                                        {user.email}
                                                    </p>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                    <div className="py-1">
                                        <button
                                            onClick={handleProfileClick}
                                            className="w-full flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors cursor-pointer text-left"
                                        >
                                            <svg className="w-4 h-4 mr-3" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                                            </svg>
                                            Profile Settings
                                        </button>
                                        <hr className="my-1" />
                                        <button
                                            onClick={handleLogout}
                                            className="w-full flex items-center px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors text-left cursor-pointer"
                                        >
                                            <svg className="w-4 h-4 mr-3" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                                            </svg>
                                            Sign out
                                        </button>
                                    </div>
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </div>
        </nav>
    );
};

const NavButton = ({ to, current, children, onClick, className }) => {
    const baseClasses = `flex items-center py-2 px-2 sm:px-3 lg:px-4 rounded-lg text-sm font-medium transition-all duration-200 border ${
        current
            ? "bg-indigo-50 text-indigo-600 border-indigo-200"
            : "text-gray-600 hover:text-indigo-600 hover:bg-indigo-50 border-transparent hover:border-indigo-200"
    }`;

    if (onClick) {
        return (
            <button
                onClick={onClick}
                className={className || baseClasses}
            >
                {children}
            </button>
        );
    }

    return (
        <Link
            to={to}
            className={baseClasses}
        >
            {children}
        </Link>
    );
};