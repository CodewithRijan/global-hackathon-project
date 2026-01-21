import React, { useState, useCallback } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import RoleToggle from '../components/RoleToggle';
import { UserRole, SignUpFormData } from '../types';
import { signUp } from '../services/authService';

const SignUpPage: React.FC = () => {
  const navigate = useNavigate();
  const [selectedRole, setSelectedRole] = useState<UserRole>(UserRole.Driver);
  const [formData, setFormData] = useState<SignUpFormData>({
    phoneNumber: '',
    fullName: '',
    password: '',
    confirmPassword: '',
    isOwner: false,
    isDriver: true,
    profilePicture: null,
  });
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const handleRoleChange = useCallback((role: UserRole) => {
    setSelectedRole(role);
    setFormData((prevData) => ({
      ...prevData,
      isOwner: role === UserRole.Partner,
      isDriver: role === UserRole.Driver,
    }));
    setError(null); // Clear errors on role change
  }, []);

  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  }, []);

  const handleFileChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFormData((prevData) => ({
        ...prevData,
        profilePicture: e.target.files![0],
      }));
    }
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    e.currentTarget.classList.add('border-blue-500', 'bg-blue-50');
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    e.currentTarget.classList.remove('border-blue-500', 'bg-blue-50');
  }, []);

  const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    e.currentTarget.classList.remove('border-blue-500', 'bg-blue-50');
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFormData((prevData) => ({
        ...prevData,
        profilePicture: e.dataTransfer.files![0],
      }));
    }
  }, []);

  const handleSubmit = useCallback(async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);
    setSuccessMessage(null);
    setIsLoading(true);

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match.');
      setIsLoading(false);
      return;
    }

    try {
      const response = await signUp(formData);
      setSuccessMessage(response);
      // In a real app, navigate to a confirmation page or login
      // navigate('/login');
    } catch (err: any) {
      setError(err.toString());
    } finally {
      setIsLoading(false);
    }
  }, [formData]);

  const nameLabel = selectedRole === UserRole.Partner ? 'Organization/Full Name' : 'Full Name';

  return (
    <div className="min-h-screen flex flex-col md:grid md:grid-cols-2 bg-gray-100">
      {/* Left Half - Visual Branding (Desktop Only) */}
      <div className="relative h-screen hidden md:flex flex-col justify-between p-12 bg-gradient-to-br from-blue-700 to-blue-900 overflow-hidden">
        {/* GalliPark branding */}
        <div className="absolute top-12 left-12 text-white font-bold text-2xl z-10">GalliPark</div>
        {/* Map-like background (simplified, could be an actual image) */}
        <div className="absolute inset-0 opacity-20" style={{ backgroundImage: "url('https://www.gstatic.com/earth/research/images/Maps_illustration_Dark_Desktop.svg')", backgroundSize: 'cover', backgroundPosition: 'center' }}></div>

        <div className="relative z-10 flex flex-col items-start justify-center flex-grow">
          {/* Motorcycle Icon */}
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-16 w-16 text-white mb-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={1.5}
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M17.618 5.618A7.989 7.989 0 0012 3c-2.43 0-4.634.978-6.22 2.618m12.44 0a7.974 7.974 0 01-2.486 3.012m-9.954-3.012A7.974 7.974 0 0112 19.999c-.771 0-1.5-.132-2.18-.387l-3.235 3.235a1 1 0 01-1.414 0l-.707-.707a1 1 0 010-1.414L6.42 16.18c-.255-.68-.387-1.409-.387-2.18 0-4.418 3.582-8 8-8s8 3.582 8 8c0 .771-.132 1.503-.387 2.18l3.235 3.235a1 1 0 010 1.414l-.707.707a1 1 0 01-1.414 0l-3.235-3.235c-.677.255-1.41.387-2.18.387" />
          </svg>
          {/* Main Title */}
          <h1 className="text-5xl font-extrabold text-white leading-tight mb-4 tracking-wide">
            Parking in Kathmandu made simple.
          </h1>
          {/* Subtitle */}
          <p className="text-lg text-white max-w-sm">
            Join thousands of riders finding safe spots in the gallis of the city.
          </p>
        </div>
      </div>

      {/* Right Half - Sign Up Form */}
      <div className="flex items-center justify-center p-4 sm:p-8 md:p-12 min-h-screen">
        <div className="bg-white p-6 sm:p-10 rounded-lg shadow-xl w-full max-w-md">
          {/* GalliPark branding in form card for mobile/consistency */}
          <div className="flex justify-between items-center mb-8">
            <span className="text-xl font-bold text-gray-800">GalliPark</span>
            {/* Go back button */}
            <button
              onClick={() => navigate(-1)}
              className="text-gray-500 hover:text-gray-700 transition-colors duration-300 flex items-center"
              type="button"
              aria-label="Go back"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-5 w-5 mr-1"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              Back
            </button>
          </div>

          <h2 className="text-3xl font-bold text-gray-800 mb-6">Create an account</h2>

          <RoleToggle selectedRole={selectedRole} onRoleChange={handleRoleChange} />

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label htmlFor="phoneNumber" className="block text-sm font-medium text-gray-700 mb-1">
                Phone Number
              </label>
              <input
                type="tel"
                id="phoneNumber"
                name="phoneNumber"
                value={formData.phoneNumber}
                onChange={handleChange}
                placeholder="+977"
                required
                className="mt-1 block w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-base"
                aria-required="true"
              />
            </div>

            <div>
              <label htmlFor="fullName" className="block text-sm font-medium text-gray-700 mb-1">
                {nameLabel}
              </label>
              <input
                type="text"
                id="fullName"
                name="fullName"
                value={formData.fullName}
                onChange={handleChange}
                placeholder={selectedRole === UserRole.Partner ? 'Organization Name or Full Name' : 'Your Full Name'}
                required
                className="mt-1 block w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-base"
                aria-required="true"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                Password
              </label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                required
                className="mt-1 block w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-base"
                aria-required="true"
              />
            </div>

            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-1">
                Confirm Password
              </label>
              <input
                type="password"
                id="confirmPassword"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                required
                className="mt-1 block w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-base"
                aria-required="true"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Profile Picture
              </label>
              <div
                className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer hover:border-blue-500 hover:bg-blue-50 transition-all duration-200 ease-in-out"
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => document.getElementById('profilePictureInput')?.click()}
                role="button"
                tabIndex={0}
                aria-label="Upload profile picture"
              >
                <div className="space-y-1 text-center">
                  {formData.profilePicture ? (
                    <img
                      src={URL.createObjectURL(formData.profilePicture)}
                      alt="Profile Preview"
                      className="mx-auto h-24 w-24 rounded-full object-cover mb-2"
                    />
                  ) : (
                    <svg
                      className="mx-auto h-12 w-12 text-gray-400"
                      stroke="currentColor"
                      fill="none"
                      viewBox="0 0 48 48"
                      aria-hidden="true"
                    >
                      <path
                        d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                        strokeWidth={2}
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                    </svg>
                  )}
                  <div className="flex text-sm text-gray-600">
                    <p className="pl-1">
                      {formData.profilePicture ? formData.profilePicture.name : 'Drag and drop or click to upload'}
                    </p>
                  </div>
                  <p className="text-xs text-gray-500">PNG, JPG, GIF up to 10MB</p>
                </div>
                <input
                  id="profilePictureInput"
                  name="profilePicture"
                  type="file"
                  className="sr-only"
                  accept="image/*"
                  onChange={handleFileChange}
                />
              </div>
            </div>

            {error && <p className="text-red-600 text-sm mt-3 text-center" role="alert">{error}</p>}
            {successMessage && <p className="text-green-600 text-sm mt-3 text-center" role="status">{successMessage}</p>}

            <button
              type="submit"
              disabled={isLoading}
              className={`w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-md text-base font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-300
              ${isLoading ? 'opacity-60 cursor-not-allowed' : ''}`}
              aria-live="polite"
              aria-busy={isLoading}
            >
              {isLoading ? (
                <svg className="animate-spin h-5 w-5 text-white mr-3" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              ) : null}
              Sign Up
            </button>
          </form>

          <div className="mt-6 text-center text-sm text-gray-600">
            Already have an account?{' '}
            <Link to="/login" className="font-medium text-blue-600 hover:text-blue-500 transition-colors duration-300">
              Login here
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SignUpPage;