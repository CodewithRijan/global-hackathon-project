import { SignUpFormData } from '../types';

/**
 * Simulates a sign-up API call.
 * In a real application, this would send data to a backend endpoint.
 * @param data The sign-up form data.
 * @returns A promise that resolves if sign-up is successful, rejects otherwise.
 */
export const signUp = async (data: SignUpFormData): Promise<string> => {
  console.log('Simulating sign-up with data:', data);

  return new Promise((resolve, reject) => {
    setTimeout(() => {
      // Simulate API success or failure
      if (data.password === data.confirmPassword) {
        // Here, you would typically send data to your Django backend
        // For example, using fetch or axios:
        // fetch('/api/signup', { method: 'POST', body: JSON.stringify(data) })
        //   .then(res => res.json())
        //   .then(json => resolve('Sign up successful!'))
        //   .catch(error => reject('Sign up failed due to network error.'));

        // For this example, we just resolve directly.
        resolve('Sign up successful! Welcome to GalliPark.');
      } else {
        reject('Passwords do not match.');
      }
    }, 1500); // Simulate network delay
  });
};
