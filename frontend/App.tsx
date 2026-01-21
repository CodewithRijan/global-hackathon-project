
import React from 'react';
import { HashRouter, Routes, Route, Navigate } from 'react-router-dom';
import Home from './pages/Home';
import Auth from './pages/Auth';
import Explorer from './pages/Explorer';
import BookingFlow from './pages/BookingFlow';
import Confirmation from './pages/Confirmation';
import Profile from './pages/Profile';
import Header from './components/Header';
import { AuthProvider, useAuth } from './context/AuthContext';

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" replace />;
  return <>{children}</>;
};

const AppRoutes = () => {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/login" element={<Auth />} />
      <Route path="/explore" element={<Explorer />} />
      <Route path="/book/:id" element={
        <ProtectedRoute>
          <BookingFlow />
        </ProtectedRoute>
      } />
      <Route path="/ticket/:bookingId" element={
        <ProtectedRoute>
          <Confirmation />
        </ProtectedRoute>
      } />
      <Route path="/profile" element={
        <ProtectedRoute>
          <Profile />
        </ProtectedRoute>
      } />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

const App: React.FC = () => {
  return (
    <AuthProvider>
      <HashRouter>
        <div className="flex flex-col min-h-screen">
          <Header />
          <main className="flex-1 overflow-x-hidden">
            <AppRoutes />
          </main>
        </div>
      </HashRouter>
    </AuthProvider>
  );
};

export default App;
