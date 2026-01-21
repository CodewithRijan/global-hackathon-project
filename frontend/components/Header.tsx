
import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Header: React.FC = () => {
  const { user, logout } = useAuth();
  const location = useLocation();

  // Hide header on Auth page as it has its own logo
  if (location.pathname === '/login') return null;

  return (
    <header className="sticky top-0 z-50 flex items-center justify-between whitespace-nowrap border-b border-solid border-slate-200 dark:border-slate-800 bg-white/90 dark:bg-slate-900/90 backdrop-blur-md px-6 lg:px-10 py-3 shadow-sm">
      <Link to="/" className="flex items-center gap-4 text-primary group">
        <div className="size-8 transition-transform group-hover:scale-110">
          <svg className="w-full h-full" fill="none" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
            <path d="M44 4H30.6666V17.3334H17.3334V30.6666H4V44H44V4Z" fill="currentColor"></path>
          </svg>
        </div>
        <h2 className="text-[#111318] dark:text-white text-xl font-bold leading-tight tracking-[-0.015em]">GalliPark</h2>
      </Link>
      
      <div className="flex flex-1 justify-end gap-6 items-center">
        <nav className="hidden md:flex items-center gap-8">
          <Link to="/explore" className="text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-primary transition-colors">Explore</Link>
          <Link to="/profile" className="text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-primary transition-colors">My Bookings</Link>
        </nav>

        <div className="flex items-center gap-3 border-l border-slate-200 dark:border-slate-800 pl-6">
          {user ? (
            <div className="flex items-center gap-3">
              <Link to="/profile" className="hidden sm:block text-right">
                <p className="text-sm font-bold dark:text-white">{user.name}</p>
                <p className="text-xs text-slate-500">Driver</p>
              </Link>
              <div className="relative group">
                <img src={user.avatar} className="size-10 rounded-full border border-slate-200 object-cover cursor-pointer" alt="avatar" />
                <div className="absolute right-0 top-full mt-2 hidden group-hover:block bg-white dark:bg-slate-800 rounded-lg shadow-xl border border-slate-200 dark:border-slate-700 p-2 min-w-[150px]">
                  <button onClick={logout} className="w-full text-left px-3 py-2 text-sm text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-md flex items-center gap-2">
                    <span className="material-symbols-outlined text-sm">logout</span>
                    Sign Out
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <Link to="/login" className="bg-primary hover:bg-primary-hover text-white px-5 py-2 rounded-lg text-sm font-bold shadow-md shadow-primary/20 transition-all">
              Sign In
            </Link>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;
