
import React, { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { PARKING_SPOTS } from '../data/mockData';
import { ParkingSpot } from '../types';

const Explorer: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSpot, setSelectedSpot] = useState<ParkingSpot | null>(null);
  const [filter, setFilter] = useState<'Available' | 'Cheapest' | 'Covered'>('Available');
  const navigate = useNavigate();

  const filteredSpots = useMemo(() => {
    let spots = PARKING_SPOTS.filter(s => 
      s.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
      s.location.toLowerCase().includes(searchQuery.toLowerCase())
    );
    if (filter === 'Cheapest') spots = [...spots].sort((a, b) => a.pricePerHour - b.pricePerHour);
    if (filter === 'Covered') spots = spots.filter(s => s.amenities.includes('Covered'));
    return spots;
  }, [searchQuery, filter]);

  return (
    <div className="h-[calc(100vh-64px)] flex relative overflow-hidden">
      {/* Sidebar List */}
      <div className="w-full max-w-sm lg:max-w-md h-full bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 flex flex-col z-10 overflow-hidden">
        <div className="p-6 border-b border-slate-100 dark:border-slate-800 flex flex-col gap-4">
          <div className="relative group">
            <span className="absolute left-4 top-1/2 -translate-y-1/2 material-symbols-outlined text-slate-400">search</span>
            <input 
              className="w-full h-12 pl-12 pr-4 bg-slate-100 dark:bg-slate-800 border-none rounded-xl focus:ring-2 focus:ring-primary focus:bg-white transition-all dark:text-white"
              placeholder="Search Kathmandu locations..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <div className="flex gap-2 overflow-x-auto no-scrollbar">
            {['Available', 'Cheapest', 'Covered'].map((f: any) => (
              <button 
                key={f}
                onClick={() => setFilter(f)}
                className={`px-4 py-2 rounded-full text-xs font-bold whitespace-nowrap transition-all ${filter === f ? 'bg-primary text-white shadow-md shadow-primary/30' : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-200'}`}
              >
                {f}
              </button>
            ))}
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4 no-scrollbar">
          <p className="text-xs font-bold text-slate-400 uppercase tracking-widest ml-2 mb-2">Nearby Parking Spots</p>
          {filteredSpots.map(spot => (
            <div 
              key={spot.id} 
              onClick={() => setSelectedSpot(spot)}
              className={`flex gap-4 p-3 rounded-2xl border transition-all cursor-pointer ${selectedSpot?.id === spot.id ? 'bg-primary/5 border-primary shadow-sm' : 'bg-white dark:bg-slate-800 border-slate-100 dark:border-slate-700 hover:border-primary/50'}`}
            >
              <div className="relative shrink-0">
                <img src={spot.imageUrl} className="size-20 rounded-xl object-cover" alt={spot.name} />
                {spot.availableSpots < 5 && (
                  <span className="absolute -bottom-1 -right-1 bg-red-500 text-white text-[10px] font-bold px-1.5 py-0.5 rounded-md border-2 border-white">
                    {spot.availableSpots} LEFT
                  </span>
                )}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex justify-between items-start mb-1">
                  <h3 className="font-bold text-slate-900 dark:text-white truncate">{spot.name}</h3>
                  <div className="flex items-center gap-1 text-xs font-bold text-yellow-500">
                    <span className="material-symbols-outlined text-[14px] filled">star</span>
                    {spot.rating}
                  </div>
                </div>
                <p className="text-xs text-slate-500 flex items-center gap-1 mb-2">
                  <span className="material-symbols-outlined text-[14px]">location_on</span>
                  {spot.distance}
                </p>
                <div className="flex justify-between items-center">
                  <p className="text-primary font-bold text-sm">Rs. {spot.pricePerHour}/hr</p>
                  <button 
                    onClick={(e) => {
                      e.stopPropagation();
                      setSelectedSpot(spot);
                    }}
                    className="px-4 py-1.5 bg-slate-100 dark:bg-slate-700 hover:bg-primary hover:text-white text-primary text-xs font-bold rounded-lg transition-all"
                  >
                    Details
                  </button>
                </div>
              </div>
            </div>
          ))}
          
          <div className="bg-gradient-to-br from-secondary/10 to-teal-500/10 p-6 rounded-3xl border border-secondary/20 mt-6 relative overflow-hidden">
             <div className="relative z-10">
                <span className="bg-secondary text-white text-[10px] font-black px-2 py-0.5 rounded-md mb-2 inline-block">EVENT NEARBY</span>
                <h4 className="text-lg font-black text-slate-900 dark:text-white mb-1 tracking-tight">Jatra Festival Parking</h4>
                <p className="text-sm text-slate-500">Special rates for today's event at Durbar Square.</p>
             </div>
             <span className="material-symbols-outlined absolute -right-4 -bottom-4 text-8xl text-secondary/10 rotate-12">confirmation_number</span>
          </div>
        </div>
      </div>

      {/* Map Content (Simulated) */}
      <div className="flex-1 relative bg-slate-200 overflow-hidden">
        <div className="absolute inset-0 opacity-80 transition-opacity">
          <img 
            src="https://lh3.googleusercontent.com/aida-public/AB6AXuDjWwzcShE5shiYRw6lrh2lej9MCcPEhqBiIj_wulrx7wmELe5_neB1jKIOJqXYSRSouwjbQq-Ngpzd9v_idCM16JAQ0qyxgy7yaBYsrRu59IlCD5hN5U69wmXokOspDD71gXShf85jbzEnzXL5ZujUTRmydk7sS1S8C87ni20RKw8r0gldiiMIL9MrKL82VIMGLHKv7goE76gGxMyEi09whBVWkgWKUzTM8jou0RQvzYKQk8FxRosZ9XISCFbB-c3sii1j6053xyE" 
            className="w-full h-full object-cover grayscale-[0.3]" 
            alt="Kathmandu Map"
          />
        </div>
        
        {/* Animated Map Pins */}
        {PARKING_SPOTS.map(spot => (
          <div 
            key={spot.id}
            onClick={() => setSelectedSpot(spot)}
            className="absolute transition-all cursor-pointer group"
            style={{ 
              top: `${40 + (Math.random() * 20)}%`, 
              left: `${30 + (Math.random() * 40)}%`,
              transform: 'translate(-50%, -100%)'
            }}
          >
            <div className={`relative flex flex-col items-center gap-1`}>
              <div className={`px-2 py-1 rounded-full text-[10px] font-black shadow-lg transition-all border-2 ${selectedSpot?.id === spot.id ? 'bg-primary text-white border-white scale-110' : 'bg-white text-slate-900 border-primary/20 group-hover:scale-105'}`}>
                Rs. {spot.pricePerHour}
              </div>
              <span className={`material-symbols-outlined text-4xl drop-shadow-xl filled transition-colors ${selectedSpot?.id === spot.id ? 'text-primary' : 'text-slate-400 group-hover:text-primary'}`}>location_on</span>
            </div>
          </div>
        ))}

        {/* Floating Map Controls */}
        <div className="absolute right-6 top-6 flex flex-col gap-2">
          <MapBtn icon="my_location" />
          <div className="flex flex-col bg-white dark:bg-slate-800 rounded-xl shadow-xl border border-slate-100 dark:border-slate-700">
             <MapBtn icon="add" />
             <div className="h-px bg-slate-100 dark:bg-slate-700 mx-2"></div>
             <MapBtn icon="remove" />
          </div>
          <MapBtn icon="layers" />
        </div>
      </div>

      {/* Spot Detail Drawer (Overlay) */}
      {selectedSpot && (
        <div className="absolute right-0 top-0 h-full w-full max-w-[480px] bg-white dark:bg-slate-900 shadow-2xl z-30 flex flex-col animate-slide-in overflow-hidden border-l border-slate-200 dark:border-slate-800">
          <header className="p-6 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between shrink-0">
             <div className="flex items-center gap-4">
                <button onClick={() => setSelectedSpot(null)} className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-full transition-all">
                  <span className="material-symbols-outlined">arrow_back</span>
                </button>
                <h2 className="text-xl font-black truncate max-w-[200px] dark:text-white tracking-tight">{selectedSpot.name}</h2>
             </div>
             <div className="flex gap-2">
                <button className="size-10 flex items-center justify-center bg-slate-100 dark:bg-slate-800 rounded-xl hover:bg-slate-200 transition-all"><span className="material-symbols-outlined">share</span></button>
                <button onClick={() => setSelectedSpot(null)} className="size-10 flex items-center justify-center bg-slate-100 dark:bg-slate-800 rounded-xl hover:bg-slate-200 transition-all"><span className="material-symbols-outlined">close</span></button>
             </div>
          </header>

          <div className="flex-1 overflow-y-auto no-scrollbar pb-32">
             <div className="relative aspect-video">
                <img src={selectedSpot.imageUrl} className="w-full h-full object-cover" alt={selectedSpot.name} />
                <div className="absolute bottom-4 right-4 bg-black/70 backdrop-blur-md text-white text-[10px] font-bold px-3 py-1.5 rounded-full flex items-center gap-2">
                  <span className="material-symbols-outlined text-sm">photo_library</span> 1/5 Photos
                </div>
             </div>

             <div className="p-8 flex flex-col gap-8">
                <div>
                  <h1 className="text-3xl font-black text-slate-900 dark:text-white mb-2 tracking-tight">{selectedSpot.name}</h1>
                  <div className="flex items-center gap-2 text-sm">
                    <span className="material-symbols-outlined text-yellow-500 filled">star</span>
                    <span className="font-black dark:text-white">{selectedSpot.rating}</span>
                    <span className="text-slate-400">({selectedSpot.reviewsCount} reviews)</span>
                    <span className="text-slate-300">•</span>
                    <button className="text-primary font-bold hover:underline">Show on map</button>
                  </div>
                </div>

                <div className="flex items-center justify-between p-5 rounded-2xl border border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50">
                   <div className="flex gap-4 items-center">
                      <img src={selectedSpot.host.avatar} className="size-14 rounded-full object-cover border-4 border-white dark:border-slate-700 shadow-sm" alt="host" />
                      <div>
                        <div className="flex items-center gap-1 mb-0.5">
                          <p className="font-black dark:text-white">{selectedSpot.host.name}</p>
                          <span className="material-symbols-outlined text-primary text-[18px] filled">verified</span>
                        </div>
                        <p className="text-xs text-slate-400">Responds in {selectedSpot.host.responseTime}</p>
                      </div>
                   </div>
                   <div className="bg-primary/10 text-primary px-3 py-1.5 rounded-full text-[10px] font-black flex items-center gap-2">
                     <span className="material-symbols-outlined text-sm">security</span> Verified Owner
                   </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                   <StatBox label="Hourly Rate" val={selectedSpot.pricePerHour} unit="NPR/hr" highlighted />
                   <StatBox label="Availability" val={selectedSpot.availableSpots} unit="Spots left" pulse />
                </div>

                <div className="space-y-4">
                   <div className="flex justify-between items-end">
                      <p className="text-sm font-bold dark:text-white">Current Status</p>
                      <p className="text-xs font-black text-secondary bg-secondary/10 px-2.5 py-1 rounded-lg">+ High Demand</p>
                   </div>
                   <div className="h-2 w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                      <div className="h-full bg-slate-900 dark:bg-primary transition-all" style={{ width: '70%' }}></div>
                   </div>
                   <p className="text-xs text-slate-400">Usually fills up by 10:00 AM daily.</p>
                </div>

                <div className="space-y-4">
                  <h3 className="font-black dark:text-white tracking-tight">Amenities</h3>
                  <div className="grid grid-cols-2 gap-3">
                    {selectedSpot.amenities.map(a => (
                      <div key={a} className="flex items-center gap-3 p-3 rounded-xl border border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/30">
                        <span className="material-symbols-outlined text-slate-900 dark:text-white text-[20px]">{a.includes('CCTV') ? 'videocam' : a.includes('Covered') ? 'roofing' : a.includes('Guarded') ? 'local_police' : 'schedule'}</span>
                        <span className="text-xs font-bold dark:text-white">{a}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="space-y-2">
                  <h3 className="font-black dark:text-white tracking-tight">About this spot</h3>
                  <p className="text-sm text-slate-500 leading-relaxed">{selectedSpot.description}</p>
                </div>
             </div>
          </div>

          <footer className="p-8 border-t border-slate-100 dark:border-slate-800 bg-white dark:bg-slate-900 shrink-0 sticky bottom-0 z-40 shadow-[0_-10px_30px_rgba(0,0,0,0.05)]">
             <div className="flex flex-col gap-6">
                <div className="flex justify-between items-center">
                   <p className="text-slate-400 text-sm">Total (est. 2 hrs)</p>
                   <p className="text-2xl font-black text-slate-900 dark:text-white tracking-tight">40 NPR</p>
                </div>
                <div className="flex gap-4">
                   <div className="flex-1 relative flex items-center">
                      <span className="absolute left-4 material-symbols-outlined text-slate-400">calendar_today</span>
                      <input readOnly className="w-full h-14 pl-12 pr-4 bg-slate-100 dark:bg-slate-800 border-none rounded-xl font-bold text-sm cursor-pointer" value="Today, 10:00 AM" />
                   </div>
                   <button 
                     onClick={() => navigate(`/book/${selectedSpot.id}`)}
                     className="flex-1 h-14 bg-primary hover:bg-primary-hover text-white font-black rounded-xl shadow-xl shadow-primary/30 flex items-center justify-center gap-3 transition-all group"
                   >
                     Book Now
                     <span className="material-symbols-outlined transition-transform group-hover:translate-x-1">arrow_forward</span>
                   </button>
                </div>
             </div>
          </footer>
        </div>
      )}
    </div>
  );
};

const MapBtn = ({ icon }: { icon: string }) => (
  <button className="size-12 flex items-center justify-center bg-white dark:bg-slate-800 rounded-xl shadow-xl border border-slate-100 dark:border-slate-700 hover:bg-slate-50 transition-all">
    <span className="material-symbols-outlined text-slate-900 dark:text-white">{icon}</span>
  </button>
);

const StatBox = ({ label, val, unit, highlighted = false, pulse = false }: { label: string; val: any; unit: string; highlighted?: boolean; pulse?: boolean }) => (
  <div className={`p-4 rounded-2xl border transition-all ${highlighted ? 'bg-primary/5 border-primary/20' : 'bg-slate-50 dark:bg-slate-800 border-slate-100 dark:border-slate-800'}`}>
    <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">{label}</p>
    <div className="flex items-center gap-2">
      {pulse && (
        <span className="relative flex h-3 w-3">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-secondary opacity-75"></span>
          <span className="relative inline-flex rounded-full h-3 w-3 bg-secondary"></span>
        </span>
      )}
      <p className={`text-2xl font-black tracking-tight ${highlighted ? 'text-primary' : 'dark:text-white'}`}>
        {val} <span className="text-xs font-bold text-slate-400 tracking-normal">{unit}</span>
      </p>
    </div>
  </div>
);

export default Explorer;
