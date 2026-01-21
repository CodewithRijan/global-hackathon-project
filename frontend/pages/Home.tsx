
import React from 'react';
import { Link } from 'react-router-dom';

const Home: React.FC = () => {
  return (
    <div className="animate-fade-in">
      {/* Hero Section */}
      <section className="relative w-full min-h-[600px] flex items-center overflow-hidden">
        <div className="absolute inset-0 z-0">
          <img 
            src="https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?auto=format&fit=crop&q=80&w=2000" 
            className="w-full h-full object-cover" 
            alt="Kathmandu street"
          />
          <div className="absolute inset-0 bg-gradient-to-r from-slate-900 via-slate-900/60 to-transparent"></div>
        </div>

        <div className="relative z-10 max-w-7xl mx-auto px-6 lg:px-10 py-24 flex flex-col gap-6">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-secondary/10 border border-secondary/20 w-fit backdrop-blur-sm">
            <span className="material-symbols-outlined text-secondary text-sm filled">verified_user</span>
            <span className="text-xs font-semibold text-secondary uppercase tracking-wider">Trusted by 10k+ Riders</span>
          </div>
          <h1 className="text-5xl lg:text-7xl font-black text-white leading-tight tracking-tight max-w-2xl">
            Parking in <span className="text-primary">Kathmandu</span>, solved.
          </h1>
          <p className="text-lg text-slate-200 max-w-xl leading-relaxed">
            Turn your empty space into passive income or find safe parking spots for your two-wheeler instantly amidst the chaos of the city.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 mt-6">
            <Link to="/explore" className="h-14 px-10 rounded-xl bg-primary hover:bg-primary-hover text-white font-bold text-lg shadow-lg hover:shadow-primary/50 transition-all flex items-center justify-center gap-3 group">
              <span className="material-symbols-outlined">search</span>
              Find Parking
              <span className="material-symbols-outlined transition-transform group-hover:translate-x-1">arrow_forward</span>
            </Link>
            <button className="h-14 px-10 rounded-xl bg-white/10 hover:bg-white/20 backdrop-blur-md border border-white/20 text-white font-bold text-lg transition-all flex items-center justify-center gap-3">
              <span className="material-symbols-outlined">add_location_alt</span>
              List Your Space
            </button>
          </div>
        </div>
      </section>

      {/* How it Works */}
      <section className="py-24 bg-white dark:bg-slate-900" id="how-it-works">
        <div className="max-w-7xl mx-auto px-6 lg:px-10">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-black text-slate-900 dark:text-white mb-4">How GalliPark Works</h2>
            <p className="text-slate-500 dark:text-slate-400 max-w-2xl mx-auto">We've streamlined the experience for both commuters and homeowners.</p>
          </div>

          <div className="grid lg:grid-cols-2 gap-12">
            {/* Rider Card */}
            <div className="bg-slate-50 dark:bg-slate-800 p-8 rounded-3xl border border-slate-100 dark:border-slate-700">
              <div className="flex items-center gap-4 mb-8">
                <div className="size-14 rounded-2xl bg-primary/10 flex items-center justify-center text-primary">
                  <span className="material-symbols-outlined text-3xl">two_wheeler</span>
                </div>
                <div>
                  <h3 className="text-2xl font-bold dark:text-white">For Riders</h3>
                  <p className="text-sm text-slate-500">Find safe parking in seconds.</p>
                </div>
              </div>
              <ul className="space-y-8">
                <StepItem num="1" title="Search Location" desc="Enter your destination to find verified spots nearby." color="bg-primary" />
                <StepItem num="2" title="View Real Photos" desc="See recent photos and check ratings before you book." color="bg-primary" />
                <StepItem num="3" title="Reserve & Pay" desc="Book instantly with cashless payments via eSewa or Khalti." color="bg-primary" />
              </ul>
            </div>

            {/* Host Card */}
            <div className="bg-slate-50 dark:bg-slate-800 p-8 rounded-3xl border border-slate-100 dark:border-slate-700">
              <div className="flex items-center gap-4 mb-8">
                <div className="size-14 rounded-2xl bg-secondary/10 flex items-center justify-center text-secondary">
                  <span className="material-symbols-outlined text-3xl">garage_home</span>
                </div>
                <div>
                  <h3 className="text-2xl font-bold dark:text-white">For Hosts</h3>
                  <p className="text-sm text-slate-500">Monetize your unused space.</p>
                </div>
              </div>
              <ul className="space-y-8">
                <StepItem num="1" title="Snap a Photo" desc="Take a clear picture of your empty space or garage." color="bg-secondary" />
                <StepItem num="2" title="Get Verified" desc="Our system validates the location to ensure safety standards." color="bg-secondary" />
                <StepItem num="3" title="Start Earning" desc="Receive payments directly to your wallet every week." color="bg-secondary" />
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Safety Standards */}
      <section className="py-24 bg-slate-50 dark:bg-slate-800">
        <div className="max-w-7xl mx-auto px-6 lg:px-10">
          <div className="text-center mb-16">
            <span className="text-primary font-bold text-sm tracking-widest uppercase mb-2 block">Safety First</span>
            <h2 className="text-4xl font-black text-slate-900 dark:text-white">Trust & Security Standards</h2>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            <SafetyCard icon="verified" title="Identity Verified" desc="Every host undergoes multi-step verification so you know who you are dealing with." />
            <SafetyCard icon="smart_toy" title="AI Spot Validation" iconColor="text-secondary" bgColor="bg-secondary/10" desc="Our system analyzes photos for lighting, gates, and accessibility features." />
            <SafetyCard icon="lock" title="Secure Payments" iconColor="text-purple-600" bgColor="bg-purple-50" desc="Payments are held securely until the session is completed. No haggling with cash." />
          </div>
        </div>
      </section>
    </div>
  );
};

const StepItem = ({ num, title, desc, color }: { num: string; title: string; desc: string; color: string }) => (
  <li className="flex gap-4">
    <div className="flex flex-col items-center">
      <div className={`size-8 rounded-full ${color} text-white flex items-center justify-center font-bold text-sm`}>{num}</div>
      <div className="w-0.5 h-full bg-slate-200 dark:bg-slate-700 my-2"></div>
    </div>
    <div>
      <h4 className="font-bold text-slate-900 dark:text-white mb-1">{title}</h4>
      <p className="text-sm text-slate-500 dark:text-slate-400">{desc}</p>
    </div>
  </li>
);

const SafetyCard = ({ icon, title, desc, iconColor = 'text-primary', bgColor = 'bg-primary/10' }: { icon: string; title: string; desc: string; iconColor?: string; bgColor?: string }) => (
  <div className="bg-white dark:bg-slate-900 p-8 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-700 hover:shadow-xl transition-all hover:-translate-y-1">
    <div className={`size-16 rounded-2xl ${bgColor} flex items-center justify-center ${iconColor} mb-6`}>
      <span className="material-symbols-outlined text-4xl filled">{icon}</span>
    </div>
    <h3 className="text-xl font-bold dark:text-white mb-3">{title}</h3>
    <p className="text-slate-500 dark:text-slate-400 leading-relaxed">{desc}</p>
  </div>
);

export default Home;
