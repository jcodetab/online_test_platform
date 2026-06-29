'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  LayoutDashboard, BookOpen, FileText, Lock, Search, 
  Trophy, Users, GraduationCap, Clock, Bell, Menu, X,
  ArrowUpRight, ChevronRight, User, LogOut, Sun, Moon, Sparkles
} from 'lucide-react';

export default function UltimateCompleteDashboard() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [currentTime, setCurrentTime] = useState('');
  const [darkMode, setDarkMode] = useState(true);

  // Raqamli soat tizimi
  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setCurrentTime(now.toLocaleTimeString("uz-UZ", { hour: '2-digit', minute: '2-digit', second: '2-digit' }));
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  const user = { first_name: "Ali", last_name: "Valiyev", role: "Foydalanuvchi" };

  // O'quv zanjiridagi 8 ta asosiy oqim chizig'i
  const streams = Array.from({ length: 8 }, (_, index) => index);

  return (
    <div className={`min-h-screen font-sans transition-colors duration-500 overflow-x-hidden relative ${
      darkMode ? 'bg-[#060814]' : 'bg-slate-50'
    }`}>
      
      {/* ─── ALGORITMLAR OQIMI VA ILM ZANJIRI FON ANIMATSIYASI ─── */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none z-0">
        
        {/* Orqa fondagi umumiy kosmik atmosfera (Neon glow) */}
        <div className={`absolute top-[20%] left-[10%] w-[500px] h-[500px] rounded-full blur-[140px] transition-colors duration-500 ${
          darkMode ? 'bg-indigo-600/15' : 'bg-indigo-600/10'
        }`} />
        <div className={`absolute bottom-[20%] right-[10%] w-[500px] h-[500px] rounded-full blur-[140px] transition-colors duration-500 ${
          darkMode ? 'bg-emerald-500/10' : 'bg-emerald-500/5'
        }`} />

        {/* DINAMIK VERTIKAL ILM CHIZIQLARI VA ULARDAGI AKTLAR */}
        <div className="absolute inset-0 flex justify-between px-12 opacity-70">
          {streams.map((id) => {
            // Har bir vertikal chiziq har xil joylashadi va har xil tezlikda harakatlanadi
            const duration = 8 + (id % 3) * 4;
            const delay = id * 0.8;

            return (
              <div key={id} className="relative h-full w-[1px] bg-gradient-to-b from-transparent via-slate-500/10 to-transparent">
                
                {/* Chiziq bo'ylab pastdan yuqoriga oqib o'tuvchi yorqin ilm tuguni (Data Node) */}
                <motion.div
                  className={`absolute left-1/2 -translate-x-1/2 w-[3px] h-24 rounded-full bg-gradient-to-b ${
                    darkMode ? 'from-indigo-400 via-purple-500 to-transparent' : 'from-indigo-600 via-indigo-400 to-transparent'
                  }`}
                  animate={{
                    top: ['100%', '-20%']
                  }}
                  transition={{
                    duration: duration,
                    repeat: Infinity,
                    ease: "linear",
                    delay: delay
                  }}
                />

                {/* Oqim ichidagi vaqti-vaqti bilan miltillab turuvchi "Muvaffaqiyat nuqtalari" */}
                <motion.div
                  className={`absolute left-1/2 -translate-x-1/2 w-2 h-2 rounded-full border shadow-[0_0_8px_rgba(99,102,241,0.8)] ${
                    id % 2 === 0 
                      ? (darkMode ? 'bg-indigo-400 border-indigo-300' : 'bg-indigo-600 border-indigo-500') 
                      : (darkMode ? 'bg-emerald-400 border-emerald-300' : 'bg-emerald-500 border-emerald-400')
                  }`}
                  style={{ top: `${20 + (id * 9) % 60}%` }}
                  animate={{
                    scale: [1, 1.8, 1],
                    opacity: [0.3, 1, 0.3]
                  }}
                  transition={{
                    duration: 3 + (id % 2) * 2,
                    repeat: Infinity,
                    ease: "easeInOut",
                    delay: id * 0.4
                  }}
                />
              </div>
            );
          })}
        </div>

        {/* Nozik matematik nuqtali arxitektura */}
        <div className={`absolute inset-0 opacity-[0.02] ${darkMode ? 'bg-[radial-gradient(#fff_1px,transparent_1px)]' : 'bg-[radial-gradient(#000_1px,transparent_1px)]'} bg-[size:40px_40px]`} />
      </div>

      {/* ─── MOBIL RESPONSIVE PANEL OVERLAY ─── */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 lg:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}
      </AnimatePresence>

      <div className="flex relative z-10">
        
        {/* ─── SIDEBAR PANEL ─── */}
        <aside className={`fixed inset-y-0 left-0 w-72 p-6 flex flex-col justify-between z-50 transform transition-all duration-300 border-r lg:translate-x-0 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        } ${darkMode ? 'bg-[#080b16]/95 border-slate-800/80 backdrop-blur-xl text-slate-100' : 'bg-white/95 border-slate-200/80 shadow-xl backdrop-blur-xl text-slate-800'}`}>
          
          <div className="space-y-8">
            <div className={`flex items-center justify-between pb-4 border-b border-dashed ${darkMode ? 'border-slate-800' : 'border-slate-200'}`}>
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center font-bold text-white text-base shadow-lg shadow-indigo-500/30">
                  TP
                </div>
                <div>
                  <span className="text-base font-bold tracking-wide block">Test Platforma</span>
                  <span className="text-[11px] text-indigo-400 font-mono tracking-widest uppercase font-semibold">Tizim v4.0</span>
                </div>
              </div>
              <button onClick={() => setSidebarOpen(false)} className="p-1.5 rounded-lg lg:hidden hover:bg-slate-500/10">
                <X size={20} />
              </button>
            </div>

            <nav className="space-y-1.5">
              {[
                { name: "Dashboard", icon: LayoutDashboard, active: true },
                { name: "Testlar", icon: BookOpen },
                { name: "Kazus testlar", icon: FileText },
                { name: "Yopiq testlar", icon: Lock },
                { name: "Testlarni qidirish", icon: Search },
                { name: "Reyting", icon: Trophy },
                { name: "Guruhlar", icon: Users },
                { name: "Olimpiadalar", icon: GraduationCap },
                { name: "Profil", icon: User },
              ].map((item, i) => (
                <a 
                  key={i} 
                  href="#" 
                  className={`flex items-center justify-between px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 group ${
                    item.active 
                      ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/20' 
                      : darkMode 
                        ? 'text-slate-400 hover:bg-slate-800 hover:text-white' 
                        : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                  }`}
                >
                  <div className="flex items-center gap-3.5">
                    <item.icon size={18} className={item.active ? 'text-white' : 'text-slate-400 group-hover:text-indigo-500 transition-colors'} />
                    <span>{item.name}</span>
                  </div>
                  {!item.active && <ChevronRight size={14} className="opacity-0 group-hover:opacity-100 transform translate-x-[-4px] group-hover:translate-x-0 transition-all text-slate-400" />}
                </a>
              ))}
            </nav>
          </div>

          <div className={`pt-4 border-t flex items-center justify-between ${darkMode ? 'border-slate-800' : 'border-slate-200'}`}>
            <div className="flex items-center gap-3">
              <div className={`h-10 w-10 rounded-xl font-bold flex items-center justify-center border ${darkMode ? 'bg-slate-900 border-slate-800 text-indigo-400' : 'bg-slate-100 border-slate-200 text-indigo-600'}`}>
                {user.first_name[0]}{user.last_name[0]}
              </div>
              <div>
                <h4 className="text-sm font-bold">{user.first_name} {user.last_name}</h4>
                <span className="text-xs text-slate-400 block">{user.role}</span>
              </div>
            </div>
            <button className="p-2 text-slate-400 hover:text-rose-500 rounded-xl hover:bg-rose-500/5 transition-colors">
              <LogOut size={16} />
            </button>
          </div>
        </aside>

        {/* ─── ASOSIY KONTENT MAYDONI ─── */}
        <main className="flex-1 lg:pl-72 flex flex-col min-w-0 text-slate-800 dark:text-slate-100">
          
          {/* HEADER */}
          <header className={`h-20 px-6 lg:px-8 flex items-center justify-between sticky top-0 z-30 border-b backdrop-blur-md transition-all duration-300 ${
            darkMode ? 'bg-[#060814]/80 border-slate-800/40 text-white' : 'bg-white/80 border-slate-200 text-slate-800'
          }`}>
            <div className="flex items-center gap-4">
              <button 
                onClick={() => setSidebarOpen(true)}
                className={`p-2 rounded-xl lg:hidden border ${darkMode ? 'border-slate-800 text-slate-400' : 'border-slate-200 text-slate-600'}`}
              >
                <Menu size={20} />
              </button>
              <div>
                <h1 className="text-xl font-bold flex items-center gap-2">
                  Asosiy oyna <Sparkles size={16} className="text-indigo-500 animate-pulse" />
                </h1>
                <p className="text-xs text-slate-400 hidden sm:block mt-0.5">Tizim faoliyati va imtihon muhiti nazorati.</p>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              <div className={`flex items-center gap-2 text-xs font-mono px-3 py-2 rounded-xl border ${
                darkMode ? 'bg-slate-900/80 border-slate-800 text-indigo-400' : 'bg-slate-100 border-slate-200 text-indigo-600'
              }`}>
                <Clock size={14} className="text-indigo-500" />
                <span>{currentTime || '00:00:00'}</span>
              </div>

              <button 
                onClick={() => setDarkMode(!darkMode)}
                className={`p-2.5 rounded-xl border transition-all ${
                  darkMode ? 'bg-slate-900 border-slate-800 text-amber-400 hover:bg-slate-800' : 'bg-slate-100 border-slate-200 text-indigo-600 hover:bg-slate-200'
                }`}
              >
                {darkMode ? <Sun size={18} /> : <Moon size={18} />}
              </button>

              <button className={`p-2.5 rounded-xl border relative ${darkMode ? 'bg-slate-900 border-slate-800 text-slate-400' : 'bg-slate-100 border-slate-200 text-slate-600'}`}>
                <Bell size={18} />
                <span className="absolute top-2.5 right-2.5 w-2 h-2 bg-indigo-600 rounded-full" />
              </button>
            </div>
          </header>

          {/* CONTENT FIELD */}
          <div className="p-6 lg:p-8 max-w-[1400px] w-full mx-auto space-y-6 relative z-10">
            
            {/* STATISTIKALAR (Glassmorphism orqali fon harakatini ko'rsatadi) */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
              {[
                { title: "Umumiy testlar", value: "75", label: "12 ta faol test", icon: BookOpen, bg: "from-blue-500/10 to-transparent", text: "text-blue-500", border: "hover:border-blue-500/30" },
                { title: "Foydalanuvchilar", value: "340", label: "+5 ta bugun qo'shildi", icon: Users, bg: "from-emerald-500/10 to-transparent", text: "text-emerald-500", border: "hover:border-emerald-500/30" },
                { title: "Mavjud Guruhlar", value: "18", label: "4 ta olimpiada guruhi", icon: Users, bg: "from-amber-500/10 to-transparent", text: "text-amber-500", border: "hover:border-amber-500/30" },
                { title: "Olimpiadalar", value: "6", label: "1 ta yaqin orada", icon: Trophy, bg: "from-rose-500/10 to-transparent", text: "text-rose-500", border: "hover:border-rose-500/30" },
              ].map((stat, i) => (
                <motion.div 
                  whileHover={{ y: -4, scale: 1.01 }}
                  key={i} 
                  className={`p-6 rounded-2xl border transition-all duration-300 flex items-center justify-between backdrop-blur-[7px] ${stat.border} ${
                    darkMode ? 'bg-[#0b0e1a]/50 border-slate-800/60 text-white' : 'bg-white/70 border-slate-200 shadow-md shadow-slate-100 text-slate-800'
                  }`}
                >
                  <div className="space-y-1">
                    <span className="text-xs font-bold uppercase tracking-wider text-slate-400">{stat.title}</span>
                    <h3 className="text-3xl font-extrabold tracking-tight">{stat.value}</h3>
                    <span className="text-xs text-slate-400 block">{stat.label}</span>
                  </div>
                  <div className={`h-12 w-12 rounded-xl bg-gradient-to-br ${stat.bg} flex items-center justify-center border ${darkMode ? 'border-slate-800' : 'border-slate-100'}`}>
                    <stat.icon size={22} className={stat.text} />
                  </div>
                </motion.div>
              ))}
            </div>

            {/* INTEGRATED DATA TABLES */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              
              {/* SHAFFAF ASOSIY JADVAL */}
              <div className={`rounded-2xl border overflow-hidden lg:col-span-2 backdrop-blur-[7px] transition-all duration-300 ${
                darkMode ? 'bg-[#0b0e1a]/50 border-slate-800/60 text-white' : 'bg-white/70 border-slate-200 shadow-md shadow-slate-100 text-slate-800'
              }`}>
                <div className={`p-5 border-b flex items-center justify-between ${darkMode ? 'border-slate-800' : 'border-slate-200'}`}>
                  <div>
                    <h3 className="font-bold text-sm uppercase tracking-wider">Yaqingi test ma'lumotlari</h3>
                    <p className="text-xs text-slate-400 mt-0.5">Tizimdagi oxirgi nazorat ishlari ro'yxati</p>
                  </div>
                  <button className="text-xs font-bold text-indigo-500 bg-indigo-500/5 border border-indigo-500/20 px-3 py-2 rounded-xl hover:bg-indigo-500/10 transition-all flex items-center gap-1">
                    Barchasi <ArrowUpRight size={14} />
                  </button>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-left border-collapse">
                    <thead>
                      <tr className={`text-[11px] font-bold uppercase tracking-wider border-b ${darkMode ? 'bg-slate-900/40 text-slate-400 border-slate-800' : 'bg-slate-50 text-slate-500 border-slate-200'}`}>
                        <th className="py-4 px-6">Test nomi</th>
                        <th className="py-4 px-6 text-center">Savollar / Vaqt</th>
                        <th className="py-4 px-6 text-right">Holat</th>
                      </tr>
                    </thead>
                    <tbody className={`divide-y text-sm ${darkMode ? 'divide-slate-800/40' : 'divide-slate-100'}`}>
                      <tr className={`transition-colors ${darkMode ? 'hover:bg-slate-900/40' : 'hover:bg-slate-50/80'}`}>
                        <td className="py-4 px-6">
                          <div className="font-bold">Yakuniy nazorat: 1-bosqich</div>
                          <div className="text-xs text-slate-400 mt-0.5 font-mono">Kategoriya: Umumiy fanlar</div>
                        </td>
                        <td className="py-4 px-6 text-center">
                          <span className="font-semibold">20 ta</span> / <span className="text-xs text-slate-400">30 min</span>
                        </td>
                        <td className="py-4 px-6 text-right">
                          <span className="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">Faol</span>
                        </td>
                      </tr>
                      <tr className={`transition-colors ${darkMode ? 'hover:bg-slate-900/40' : 'hover:bg-slate-50/80'}`}>
                        <td className="py-4 px-6">
                          <div className="font-bold">Saralash imtihoni (Demo)</div>
                          <div className="text-xs text-slate-400 mt-0.5 font-mono">Kategoriya: Kirish testlari</div>
                        </td>
                        <td className="py-4 px-6 text-center">
                          <span className="font-semibold">50 ta</span> / <span className="text-xs text-slate-400">60 min</span>
                        </td>
                        <td className="py-4 px-6 text-right">
                          <span className="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-bold bg-slate-500/10 text-slate-400 border border-slate-500/10">Yopilgan</span>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              {/* SIDE PANELS */}
              <div className="space-y-6">
                <div className={`p-5 rounded-2xl border backdrop-blur-[7px] ${darkMode ? 'bg-[#0b0e1a]/50 border-slate-800/60 text-white' : 'bg-white/70 border-slate-200 shadow-md text-slate-800'}`}>
                  <h3 className="font-bold text-sm mb-4 flex items-center gap-2 uppercase tracking-wider">
                    <Users size={16} className="text-indigo-500" /> Guruhlar
                  </h3>
                  <div className={`flex items-center justify-between p-3.5 rounded-xl border ${darkMode ? 'bg-slate-900/50 border-slate-800' : 'bg-slate-50 border-slate-100'}`}>
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-xl bg-indigo-500/10 flex items-center justify-center text-indigo-500 font-bold text-xs">FN</div>
                      <span className="text-xs font-bold">FN-101 Guruhi</span>
                    </div>
                    <span className="text-xs font-mono bg-indigo-500/10 text-indigo-500 px-2.5 py-1 rounded-lg border border-indigo-500/10">24 talaba</span>
                  </div>
                </div>

                <div className={`p-5 rounded-2xl border backdrop-blur-[7px] ${darkMode ? 'bg-[#0b0e1a]/50 border-slate-800/60 text-white' : 'bg-white/70 border-slate-200 shadow-md text-slate-800'}`}>
                  <h3 className="font-bold text-sm mb-4 flex items-center gap-2 uppercase tracking-wider">
                    <Trophy size={16} className="text-amber-500" /> Olimpiadalar
                  </h3>
                  <div className={`flex items-center justify-between p-3.5 rounded-xl border ${darkMode ? 'bg-slate-900/50 border-slate-800' : 'bg-slate-50 border-slate-100'}`}>
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-xl bg-amber-500/10 flex items-center justify-center text-amber-400 text-xs">✨</div>
                      <span className="text-xs font-bold">Matematika fani</span>
                    </div>
                    <span className="text-xs font-mono bg-emerald-500/10 text-emerald-400 px-2.5 py-1 rounded-lg border border-emerald-500/20">Aktiv</span>
                  </div>
                </div>
              </div>

            </div>

          </div>
        </main>
      </div>
    </div>
  );
}
