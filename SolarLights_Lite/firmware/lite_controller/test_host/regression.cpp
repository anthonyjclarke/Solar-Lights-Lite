#include <cassert>
#include <cstdio>
#include "schedule.h"
using namespace lite;
static Scheduler base() { Scheduler s; s.cfg.selfTestS=0; s.cfg.debounceS=5; s.cfg.capPct=5; s.cfg.allNightPct=5; s.cfg.predawn=false; s.begin(true,true); return s; }
int main() {
  { auto s=base(); for(int t=0;t<4;t++) assert(s.step(1,3.8,true,false)==0); s.step(1,3.8,false,false); assert(!s.night); for(int t=0;t<5;t++)s.step(1,3.8,true,false); assert(s.night); }
  { auto s=base(); for(int t=0;t<14*3600;t++) {auto p=s.step(1,3.8,true,false); assert(p<=5); if(t>10)assert(p==5);} for(int t=0;t<10;t++)s.step(1,3.8,false,true); assert(!s.night && s.pct==0); }
  { auto s=base(); s.cfg.selfTestS=10; assert(s.step(1,3.8,false,true)<=5); s.button(); assert(s.step(1,3.8,false,true)<=5); }
  { auto s=base(); for(int t=0;t<20;t++)s.step(1,3.8,true,false); for(int t=0;t<29;t++)s.step(1,3.2,true,false); assert(s.state!=LVC); assert(s.step(1,3.2,true,false)==0 && s.state==LVC); s.button(); for(int t=0;t<100;t++)assert(s.step(1,3.8,true,false)==0); for(int t=0;t<5;t++)s.step(1,3.8,false,true); assert(s.state==DAY); }
  { auto s=base(); s.cfg.selfTestS=10; s.button(); assert(s.step(1,3.2,false,true)==0); }
  { auto s=base(); for(int t=0;t<20;t++)s.step(1,3.8,true,false); for(int t=0;t<20;t++)s.step(1,3.4,true,false); assert(s.pct==2); }
  { auto s=base(); s.cfg.selfTestS=0; s.step(8,3.8,true,false); assert(s.night); for(int t=0;t<4;t++)s.step(8,3.2,true,false); assert(s.state==LVC && s.pct==0); }
  { auto s=base(); s.begin(false,false); s.cfg.fallbackEveningS=30; for(int t=0;t<80;t++)s.step(1,3.8,true,false); assert(s.pct==0); }
  { Scheduler s; s.cfg.selfTestS=0; s.cfg.debounceS=5; s.cfg.predawn=false; s.cfg.capPct=100; s.cfg.allNightPct=100; s.begin(true,true); /* mirrors main.cpp NIGHT_DUTY_PCT */ for(int t=0;t<10;t++)s.step(1,3.8,true,false); for(int t=0;t<200;t++)s.step(1,3.8,true,false); assert(s.pct==100); for(int t=0;t<200;t++)s.step(1,3.4,true,false); assert(s.pct==50); }
  puts("PASS: 9 regression groups (debounce, 14h dusk-to-dawn, test cap, LVC/recovery, low startup, low brightness, slow tick, evening mode, shipped 100% default)");
}
