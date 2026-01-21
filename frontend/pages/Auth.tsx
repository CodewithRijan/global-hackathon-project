
import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Auth: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    if (email) {
      login(email);
      navigate('/explore');
    }
  };

  return (
    <div className="flex min-h-screen">
      {/* Left Panel */}
      <div className="hidden lg:flex w-1/2 relative bg-slate-100 items-center justify-center overflow-hidden">
        <div 
          className="absolute inset-0 bg-cover bg-center" 
          style={{ backgroundImage: `url('https://images.unsplash.com/photo-1558981403-c5f9899a28bc?auto=format&fit=crop&q=80&w=800')` }}
        ></div>
        <div className="absolute inset-0 bg-gradient-to-t from-slate-900 via-slate-900/20 to-transparent"></div>
        <div className="relative z-10 w-full max-w-lg p-12 mt-auto">
          <div className="size-12 bg-white rounded-lg flex items-center justify-center text-primary mb-6">
            <span className="material-symbols-outlined text-3xl">two_wheeler</span>
          </div>
          <h2 className="text-white text-4xl font-black leading-tight mb-4 tracking-tight">Parking in Kathmandu made simple.</h2>
          <p className="text-slate-200 text-lg">Join thousands of riders finding safe spots in the gallis of the city.</p>
        </div>
      </div>

      {/* Right Panel */}
      <div className="w-full lg:w-1/2 flex flex-col bg-white dark:bg-slate-900 relative">
        <div className="absolute top-0 left-0 w-full p-8 lg:p-12">
          <Link to="/" className="flex items-center gap-3 text-primary">
             <div className="size-8">
               <svg className="w-full h-full" fill="none" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
                  <path d="M44 4H30.6666V17.3334H17.3334V30.6666H4V44H44V4Z" fill="currentColor"></path>
                </svg>
             </div>
             <h2 className="text-slate-900 dark:text-white text-xl font-black tracking-tight">GalliPark</h2>
          </Link>
        </div>

        <div className="flex-1 flex flex-col justify-center max-w-md mx-auto w-full px-8 py-20">
          <div className="mb-10">
            <h1 className="text-4xl font-black text-slate-900 dark:text-white mb-3 tracking-tight">Welcome Back</h1>
            <p className="text-slate-500 dark:text-slate-400">Log in to manage your parking spots and bookings.</p>
          </div>

          <form onSubmit={handleLogin} className="space-y-6">
            <div className="space-y-2">
              <label className="text-sm font-bold text-slate-700 dark:text-slate-300">Email or Phone Number</label>
              <input 
                type="text"
                required
                className="w-full h-14 px-4 rounded-xl border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 focus:ring-2 focus:ring-primary focus:border-transparent transition-all outline-none dark:text-white"
                placeholder="Enter your email or phone"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <div className="flex justify-between">
                <label className="text-sm font-bold text-slate-700 dark:text-slate-300">Password</label>
                <Link to="#" className="text-sm font-bold text-primary hover:underline">Forgot?</Link>
              </div>
              <div className="relative">
                <input 
                  type="password"
                  required
                  className="w-full h-14 px-4 rounded-xl border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 focus:ring-2 focus:ring-primary focus:border-transparent transition-all outline-none dark:text-white"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
                <button type="button" className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400">
                  <span className="material-symbols-outlined">visibility</span>
                </button>
              </div>
            </div>

            <button type="submit" className="w-full h-14 bg-primary hover:bg-primary-hover text-white font-black rounded-xl shadow-lg shadow-primary/30 transition-all flex items-center justify-center gap-2">
              Sign In
            </button>
          </form>

          <div className="relative my-10">
            <div className="absolute inset-0 flex items-center"><span className="w-full border-t border-slate-200 dark:border-slate-700"></span></div>
            <div className="relative flex justify-center text-sm"><span className="bg-white dark:bg-slate-900 px-4 text-slate-400">Or continue with</span></div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <SocialBtn icon="https://www.google.com/favicon.ico" label="Google" />
            <SocialBtn icon="https://www.facebook.com/favicon.ico" label="Facebook" />
          </div>

          <p className="mt-10 text-center text-slate-500">
            Don't have an account? <Link to="#" className="text-primary font-bold hover:underline">Sign up</Link>
          </p>
        </div>
      </div>
    </div>
  );
};

const SocialBtn = ({ icon, label }: { icon: string; label: string }) => (
  <button className="flex items-center justify-center gap-3 h-14 rounded-xl border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors">
    <img src={icon} className="size-5" alt={label} />
    <span className="font-bold text-slate-700 dark:text-white">{label}</span>
  </button>
);

export default Auth;
