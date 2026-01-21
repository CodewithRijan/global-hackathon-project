
import React, { useState } from 'react';
import { PARKING_SPOTS } from '../data/mockData';

const Profile: React.FC = () => {
  const [tab, setTab] = useState<'Favorites' | 'History'>('Favorites');

  return (
    <div className="max-w-7xl mx-auto px-6 lg:px-10 py-12 animate-fade-in">
       <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-12">
          <div>
             <div className="flex items-center gap-2 text-sm font-bold text-slate-400 mb-2">
               <span>Home</span> <span className="material-symbols-outlined text-sm">chevron_right</span>
               <span className="text-primary">My Activity</span>
             </div>
             <h1 className="text-4xl lg:text-5xl font-black text-slate-900 dark:text-white tracking-tight">My Activity</h1>
             <p className="text-slate-500 mt-2 text-lg">Manage your saved spots and view your parking history.</p>
          </div>
          <div className="relative w-full max-w-xs">
             <span className="absolute left-4 top-1/2 -translate-y-1/2 material-symbols-outlined text-slate-400">search</span>
             <input className="w-full h-12 pl-12 pr-4 bg-slate-100 dark:bg-slate-800 border-none rounded-xl text-sm font-bold focus:ring-2 focus:ring-primary focus:bg-white transition-all dark:text-white" placeholder="Search my history..." />
          </div>
       </div>

       <div className="border-b border-slate-200 dark:border-slate-800 mb-10">
          <nav className="flex gap-10">
             {['Favorites', 'History'].map((t: any) => (
               <button 
                 key={t}
                 onClick={() => setTab(t)}
                 className={`pb-4 px-2 text-sm font-black transition-all border-b-4 ${tab === t ? 'border-primary text-primary' : 'border-transparent text-slate-400 hover:text-slate-600'}`}
               >
                 <span className="flex items-center gap-2">
                    <span className={`material-symbols-outlined text-lg ${tab === t ? 'filled' : ''}`}>{t === 'Favorites' ? 'favorite' : 'history'}</span>
                    {t}
                 </span>
               </button>
             ))}
          </nav>
       </div>

       {tab === 'Favorites' ? (
         <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {PARKING_SPOTS.map(spot => (
              <div key={spot.id} className="group bg-white dark:bg-slate-900 rounded-3xl border border-slate-100 dark:border-slate-800 overflow-hidden hover:shadow-2xl hover:-translate-y-1 transition-all">
                 <div className="relative h-56">
                    <img src={spot.imageUrl} className="w-full h-full object-cover transition-transform group-hover:scale-110 duration-700" alt={spot.name} />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent"></div>
                    <button className="absolute top-4 right-4 size-10 bg-white/90 backdrop-blur rounded-full text-red-500 hover:scale-110 transition-all flex items-center justify-center shadow-lg"><span className="material-symbols-outlined filled">favorite</span></button>
                    <div className="absolute bottom-4 left-4 text-white">
                       <div className="inline-flex items-center gap-1 bg-primary/90 backdrop-blur px-2 py-0.5 rounded text-[10px] font-black mb-1"><span className="material-symbols-outlined text-[12px] filled">star</span> {spot.rating}</div>
                       <h3 className="text-xl font-black tracking-tight">{spot.name}</h3>
                    </div>
                 </div>
                 <div className="p-6">
                    <div className="flex justify-between items-center mb-6">
                       <div className="flex items-center text-slate-400 text-xs font-bold gap-1"><span className="material-symbols-outlined text-lg">location_on</span> {spot.location.split(',')[0]}</div>
                       <p className="font-black text-slate-900 dark:text-white">NRs {spot.pricePerHour}<span className="text-xs text-slate-400 font-bold">/hr</span></p>
                    </div>
                    <button className="w-full h-12 bg-primary hover:bg-primary-hover text-white font-black rounded-xl transition-all flex items-center justify-center gap-3">
                       <span className="material-symbols-outlined text-[20px]">bolt</span> Quick Book
                    </button>
                 </div>
              </div>
            ))}
         </div>
       ) : (
         <div className="bg-white dark:bg-slate-900 rounded-3xl border border-slate-100 dark:border-slate-800 overflow-hidden shadow-sm">
            <div className="overflow-x-auto">
               <table className="w-full text-left">
                  <thead className="bg-slate-50 dark:bg-slate-800/50 border-b border-slate-100 dark:border-slate-800">
                     <tr className="text-[10px] font-black text-slate-400 uppercase tracking-widest">
                        <th className="px-8 py-6">Date & Time</th>
                        <th className="px-8 py-6">Location</th>
                        <th className="px-8 py-6 text-center">Duration</th>
                        <th className="px-8 py-6">Cost</th>
                        <th className="px-8 py-6">Status</th>
                        <th className="px-8 py-6 text-right">Actions</th>
                     </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-50 dark:divide-slate-800">
                     <HistoryRow date="Oct 24, 2023" time="2:00 PM - 4:00 PM" name="Baneshwor Heights" slot="Slot A-12" dur="2 hrs" cost="50" status="Completed" />
                     <HistoryRow date="Oct 20, 2023" time="9:00 AM - 1:00 PM" name="Thamel Tourist Hub" slot="Slot B-05" dur="4 hrs" cost="100" status="Completed" />
                     <HistoryRow date="Oct 15, 2023" time="10:30 AM - 11:30 AM" name="Durbar Marg Basement" slot="Slot C-22" dur="1 hr" cost="20" status="Cancelled" />
                  </tbody>
               </table>
            </div>
         </div>
       )}
    </div>
  );
};

const HistoryRow = ({ date, time, name, slot, dur, cost, status }: any) => (
  <tr className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
    <td className="px-8 py-6">
       <div className="font-black dark:text-white text-sm">{date}</div>
       <div className="text-xs text-slate-400">{time}</div>
    </td>
    <td className="px-8 py-6">
       <div className="flex items-center gap-4">
          <div className="size-10 bg-slate-100 dark:bg-slate-800 rounded-xl overflow-hidden shrink-0">
             <img src={`https://picsum.photos/seed/${name}/100/100`} className="w-full h-full object-cover" alt="spot" />
          </div>
          <div>
             <div className="font-black text-sm dark:text-white">{name}</div>
             <div className="text-xs text-slate-400">{slot}</div>
          </div>
       </div>
    </td>
    <td className="px-8 py-6 text-center text-slate-500 font-bold text-sm">{dur}</td>
    <td className="px-8 py-6 font-black dark:text-white text-sm">NRs {cost}</td>
    <td className="px-8 py-6">
       <span className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-wider ${status === 'Completed' ? 'bg-secondary/10 text-secondary' : 'bg-slate-100 text-slate-400'}`}>
          {status}
       </span>
    </td>
    <td className="px-8 py-6 text-right">
       <div className="flex items-center justify-end gap-3">
          <button className="size-10 flex items-center justify-center bg-slate-100 dark:bg-slate-800 text-slate-400 hover:text-slate-600 rounded-xl transition-all"><span className="material-symbols-outlined text-lg">receipt_long</span></button>
          <button className="px-4 py-2 bg-primary/10 text-primary hover:bg-primary hover:text-white text-[10px] font-black uppercase rounded-xl transition-all">
             {status === 'Completed' ? 'Book Again' : 'Details'}
          </button>
       </div>
    </td>
  </tr>
);

export default Profile;
