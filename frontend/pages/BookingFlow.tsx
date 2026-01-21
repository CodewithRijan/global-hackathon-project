
import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { PARKING_SPOTS } from '../data/mockData';
import { PaymentMethod } from '../types';

const BookingFlow: React.FC = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const spot = PARKING_SPOTS.find(s => s.id === id);
  const [method, setMethod] = useState<PaymentMethod>(PaymentMethod.ESEWA);
  const [duration, setDuration] = useState(2);
  const [plate, setPlate] = useState('BA 2 PA 1234');

  if (!spot) return <div>Spot not found</div>;

  const cost = duration * spot.pricePerHour + 10; // 10 is service fee

  const handlePay = () => {
    // Simulate booking creation
    const bookingId = Math.random().toString(36).substr(2, 9).toUpperCase();
    navigate(`/ticket/${bookingId}`, { state: { spot, duration, cost, plate } });
  };

  return (
    <div className="max-w-7xl mx-auto px-6 lg:px-10 py-12 animate-fade-in">
      <div className="mb-10 flex flex-col gap-2">
         <div className="flex items-center gap-3 text-sm font-bold text-slate-400">
           <span>Search</span> <span className="material-symbols-outlined text-sm">chevron_right</span>
           <span className="text-primary">Payment Details</span> <span className="material-symbols-outlined text-sm">chevron_right</span>
           <span>Confirmation</span>
         </div>
         <h1 className="text-4xl lg:text-5xl font-black tracking-tight dark:text-white">Complete your booking</h1>
         <p className="text-slate-500">Step 2 of 3: Secure your spot</p>
      </div>

      <div className="grid lg:grid-cols-3 gap-10">
        <div className="lg:col-span-2 space-y-8">
          {/* Section: Date & Time */}
          <section className="bg-white dark:bg-slate-900 p-8 rounded-3xl border border-slate-100 dark:border-slate-800 shadow-sm">
             <h3 className="text-xl font-black mb-6 flex items-center gap-3 dark:text-white">
                <span className="material-symbols-outlined text-primary filled">calendar_month</span>
                Date & Time
             </h3>
             <div className="grid md:grid-cols-2 gap-10">
                <div className="space-y-4">
                   <div className="flex justify-between items-center mb-4">
                      <button className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-full transition-all"><span className="material-symbols-outlined">chevron_left</span></button>
                      <p className="font-black dark:text-white">October 2023</p>
                      <button className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-full transition-all"><span className="material-symbols-outlined">chevron_right</span></button>
                   </div>
                   <div className="grid grid-cols-7 gap-1 text-center">
                      {['S','M','T','W','T','F','S'].map(d => <span key={d} className="text-[10px] font-black text-slate-400 py-2">{d}</span>)}
                      {Array.from({length: 31}).map((_, i) => (
                        <button key={i} className={`size-10 flex items-center justify-center rounded-full text-sm font-bold transition-all ${i + 1 === 24 ? 'bg-primary text-white shadow-lg' : 'hover:bg-slate-100 dark:hover:bg-slate-800 dark:text-white'}`}>
                          {i + 1}
                        </button>
                      ))}
                   </div>
                </div>
                <div className="space-y-6">
                   <InputGroup label="Arrival Time" type="select" options={['08:00 AM', '09:00 AM', '10:00 AM', '11:00 AM']} />
                   <InputGroup label="Duration" type="select" options={['1 Hour', '2 Hours', '3 Hours', '4 Hours']} onChange={(e: any) => setDuration(parseInt(e.target.value))} />
                   <InputGroup label="Vehicle Plate No." type="text" value={plate} onChange={(e: any) => setPlate(e.target.value)} />
                </div>
             </div>
          </section>

          {/* Section: Payment Method */}
          <section className="bg-white dark:bg-slate-900 p-8 rounded-3xl border border-slate-100 dark:border-slate-800 shadow-sm">
             <h3 className="text-xl font-black mb-6 flex items-center gap-3 dark:text-white">
                <span className="material-symbols-outlined text-primary filled">payments</span>
                Payment Method
             </h3>
             <div className="grid grid-cols-3 gap-4 mb-8">
                <PaymentBtn id={PaymentMethod.ESEWA} label="eSewa Wallet" active={method === PaymentMethod.ESEWA} onClick={() => setMethod(PaymentMethod.ESEWA)} img="https://www.esewa.com.np/common/images/esewa_logo.png" />
                <PaymentBtn id={PaymentMethod.KHALTI} label="Khalti Wallet" active={method === PaymentMethod.KHALTI} onClick={() => setMethod(PaymentMethod.KHALTI)} img="https://khalti.com/static/khalti-logo.png" />
                <PaymentBtn id={PaymentMethod.CARD} label="Card" active={method === PaymentMethod.CARD} onClick={() => setMethod(PaymentMethod.CARD)} icon="credit_card" />
             </div>

             {method === PaymentMethod.CARD && (
               <div className="space-y-6 animate-fade-in">
                  <InputGroup label="Card Number" type="text" placeholder="0000 0000 0000 0000" />
                  <div className="grid grid-cols-2 gap-4">
                    <InputGroup label="Expiry Date" type="text" placeholder="MM/YY" />
                    <InputGroup label="CVV" type="text" placeholder="123" />
                  </div>
               </div>
             )}
          </section>

          <button 
            onClick={handlePay}
            className="w-full h-16 bg-primary hover:bg-primary-hover text-white text-xl font-black rounded-2xl shadow-2xl shadow-primary/30 flex items-center justify-center gap-4 transition-all"
          >
            Pay & Book NPR {cost}
            <span className="material-symbols-outlined text-2xl">lock</span>
          </button>
          <div className="flex justify-center items-center gap-2 text-slate-400 text-xs font-bold">
            <span className="material-symbols-outlined text-sm">verified_user</span>
            PAYMENTS ARE SECURE AND ENCRYPTED
          </div>
        </div>

        {/* Sidebar Summary */}
        <div className="space-y-6">
           <div className="lg:sticky lg:top-24 bg-white dark:bg-slate-900 rounded-3xl border border-slate-100 dark:border-slate-800 shadow-xl overflow-hidden">
              <div className="relative h-48">
                 <img src={spot.imageUrl} className="w-full h-full object-cover" alt="spot" />
                 <div className="absolute top-4 right-4 bg-white/90 backdrop-blur-md px-3 py-1.5 rounded-full text-xs font-black shadow-lg flex items-center gap-2 text-slate-900">
                    <span className="material-symbols-outlined text-primary text-sm filled">star</span> {spot.rating}
                 </div>
              </div>
              <div className="p-8 space-y-8">
                 <div>
                    <h4 className="text-2xl font-black dark:text-white mb-2 tracking-tight">{spot.name}</h4>
                    <p className="text-slate-500 text-sm flex items-center gap-2">
                       <span className="material-symbols-outlined text-lg">location_on</span>
                       {spot.location}
                    </p>
                 </div>
                 <div className="h-px bg-slate-100 dark:bg-slate-800"></div>
                 <div className="flex justify-between items-center text-sm">
                    <div className="space-y-1">
                       <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">START</p>
                       <p className="font-bold dark:text-white">Oct 24, 09:00 AM</p>
                    </div>
                    <span className="material-symbols-outlined text-slate-300">arrow_forward</span>
                    <div className="text-right space-y-1">
                       <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">END</p>
                       <p className="font-bold dark:text-white">Oct 24, {9 + duration}:00 AM</p>
                    </div>
                 </div>
                 <div className="bg-primary/5 p-4 rounded-2xl flex items-start gap-4">
                    <span className="material-symbols-outlined text-primary">info</span>
                    <p className="text-xs font-bold text-slate-600 dark:text-slate-400 leading-relaxed">Please arrive 5 mins early. Gate code is #8899.</p>
                 </div>
                 <div className="h-px bg-slate-100 dark:bg-slate-800"></div>
                 <div className="space-y-4">
                    <PriceRow label={`Rate (${duration} hrs × NPR ${spot.pricePerHour})`} val={`NPR ${duration * spot.pricePerHour}`} />
                    <PriceRow label="Service fee" val="NPR 10" />
                    <PriceRow label="Early bird discount" val="- NPR 0" color="text-secondary" />
                    <div className="h-px bg-slate-100 dark:bg-slate-800 pt-2"></div>
                    <div className="flex justify-between items-end">
                       <span className="text-lg font-bold dark:text-white">Total (NPR)</span>
                       <span className="text-4xl font-black text-primary tracking-tight">{cost}</span>
                    </div>
                 </div>
              </div>
           </div>
        </div>
      </div>
    </div>
  );
};

const InputGroup = ({ label, type, options, placeholder, value, onChange }: any) => (
  <div className="space-y-2">
    <label className="text-xs font-black text-slate-400 uppercase tracking-widest">{label}</label>
    {type === 'select' ? (
      <select onChange={onChange} className="w-full h-14 rounded-xl border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800 font-bold focus:ring-2 focus:ring-primary transition-all dark:text-white">
        {options.map((o: any) => <option key={o} value={o.split(' ')[0]}>{o}</option>)}
      </select>
    ) : (
      <input 
        className="w-full h-14 rounded-xl border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800 font-bold focus:ring-2 focus:ring-primary transition-all dark:text-white placeholder:text-slate-300" 
        placeholder={placeholder} 
        value={value} 
        onChange={onChange}
      />
    )}
  </div>
);

const PaymentBtn = ({ id, label, active, onClick, img, icon }: any) => (
  <button 
    onClick={onClick}
    className={`p-4 rounded-2xl border flex flex-col items-center justify-center gap-2 transition-all h-28 ${active ? 'bg-primary/5 border-primary shadow-sm' : 'bg-white dark:bg-slate-800 border-slate-100 dark:border-slate-800 hover:border-primary/50'}`}
  >
    {img ? (
      <div className="h-10 w-full bg-contain bg-center bg-no-repeat filter grayscale opacity-60 contrast-125" style={{ backgroundImage: `url('${img}')` }}></div>
    ) : (
      <span className="material-symbols-outlined text-4xl text-slate-400">{icon}</span>
    )}
    <span className={`text-[10px] font-black uppercase tracking-widest ${active ? 'text-primary' : 'text-slate-400'}`}>{label}</span>
  </button>
);

const PriceRow = ({ label, val, color = 'text-slate-500' }: { label: string; val: string; color?: string }) => (
  <div className="flex justify-between text-sm">
    <span className="text-slate-400 font-bold">{label}</span>
    <span className={`font-black ${color}`}>{val}</span>
  </div>
);

export default BookingFlow;
