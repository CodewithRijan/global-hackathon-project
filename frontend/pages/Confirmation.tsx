
import React from 'react';
import { useLocation, useParams, Link } from 'react-router-dom';

const Confirmation: React.FC = () => {
  const { bookingId } = useParams();
  const location = useLocation();
  const { spot, duration, cost, plate } = location.state || {};

  if (!spot) return <div className="p-20 text-center">No data found for this booking. <Link to="/explore" className="text-primary font-bold">Go back</Link></div>;

  return (
    <div className="max-w-4xl mx-auto px-6 py-12 flex flex-col items-center gap-10 animate-fade-in">
       <div className="flex flex-col items-center text-center gap-4">
          <div className="size-20 rounded-full bg-secondary/10 text-secondary flex items-center justify-center animate-bounce-slow">
            <span className="material-symbols-outlined text-5xl filled">check_circle</span>
          </div>
          <h1 className="text-4xl lg:text-5xl font-black text-slate-900 dark:text-white tracking-tight">Booking Confirmed!</h1>
          <p className="text-slate-500 text-lg max-w-md">Your parking spot has been successfully reserved. Please show the QR code below at the entry gate.</p>
       </div>

       {/* Digital Ticket */}
       <div className="w-full max-w-md bg-white dark:bg-slate-900 rounded-[2.5rem] shadow-2xl border border-slate-100 dark:border-slate-800 overflow-hidden relative group">
          <div className="bg-white p-12 flex flex-col items-center gap-6 relative border-b border-dashed border-slate-200">
             {/* Ticket Holes */}
             <div className="absolute -bottom-4 -left-4 size-8 bg-background-light dark:bg-background-dark rounded-full"></div>
             <div className="absolute -bottom-4 -right-4 size-8 bg-background-light dark:bg-background-dark rounded-full"></div>
             
             <h3 className="text-xs font-black text-slate-400 uppercase tracking-widest opacity-60">Entry Token</h3>
             <div className="size-60 p-4 border-4 border-slate-900 rounded-[2rem] bg-white transition-transform group-hover:scale-105 duration-500">
                <img src="https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=GalliPark-123" className="w-full h-full" alt="QR Token" />
             </div>
             <div className="flex items-center gap-2 text-slate-400 text-xs font-bold">
               <span className="material-symbols-outlined text-lg">brightness_high</span>
               INCREASE BRIGHTNESS FOR SCANNING
             </div>
          </div>

          <div className="p-10 space-y-8">
             <div className="space-y-6">
                <DetailRow label="Location" val={spot.name} icon="location_on" highlighted />
                <DetailRow label="Time Slot" val={`Oct 24, 10:00 AM - ${10 + duration}:00 PM`} />
                <DetailRow label="Vehicle Plate" val={plate} font="font-mono" />
                <DetailRow label="Booking ID" val={`#${bookingId}`} />
             </div>

             <div className="relative h-32 rounded-3xl overflow-hidden shadow-inner cursor-pointer group/map">
                <img src="https://lh3.googleusercontent.com/aida-public/AB6AXuDjWwzcShE5shiYRw6lrh2lej9MCcPEhqBiIj_wulrx7wmELe5_neB1jKIOJqXYSRSouwjbQq-Ngpzd9v_idCM16JAQ0qyxgy7yaBYsrRu59IlCD5hN5U69wmXokOspDD71gXShf85jbzEnzXL5ZujUTRmydk7sS1S8C87ni20RKw8r0gldiiMIL9MrKL82VIMGLHKv7goE76gGxMyEi09whBVWkgWKUzTM8jou0RQvzYKQk8FxRosZ9XISCFbB-c3sii1j6053xyE" className="w-full h-full object-cover transition-transform group-hover/map:scale-110" alt="map" />
                <div className="absolute inset-0 bg-black/20 flex items-center justify-center">
                   <div className="bg-white/90 backdrop-blur px-4 py-2 rounded-full font-bold text-xs shadow-xl flex items-center gap-2">
                     <span className="material-symbols-outlined text-sm text-primary">directions</span>
                     VIEW ON MAP
                   </div>
                </div>
             </div>

             <div className="flex flex-col gap-4 pt-4">
                <button className="h-14 bg-primary hover:bg-primary-hover text-white font-black rounded-2xl shadow-xl shadow-primary/30 flex items-center justify-center gap-3 transition-all transform active:scale-[0.98]">
                   <span className="material-symbols-outlined">near_me</span>
                   Get Directions
                </button>
                <button className="h-14 border-2 border-slate-100 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800 font-bold dark:text-white rounded-2xl transition-all flex items-center justify-center gap-3">
                   <span className="material-symbols-outlined">download</span>
                   Save Ticket
                </button>
             </div>
          </div>
       </div>

       <div className="flex items-center gap-4 text-sm font-bold text-slate-400">
          <button className="hover:text-red-500 transition-colors flex items-center gap-2"><span className="material-symbols-outlined text-lg">cancel</span> Cancel Booking</button>
          <span className="h-4 w-px bg-slate-200"></span>
          <button className="hover:text-primary transition-colors flex items-center gap-2"><span className="material-symbols-outlined text-lg">help</span> Need Help?</button>
       </div>
    </div>
  );
};

const DetailRow = ({ label, val, icon, highlighted = false, font = '' }: any) => (
  <div className="flex justify-between items-start border-b border-slate-50 dark:border-slate-800 pb-4">
    <div className="flex flex-col gap-1">
      <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">{label}</span>
      <div className={`flex items-center gap-2 font-black dark:text-white ${highlighted ? 'text-primary' : ''} ${font}`}>
        {icon && <span className="material-symbols-outlined text-lg">{icon}</span>}
        {val}
      </div>
    </div>
  </div>
);

export default Confirmation;
