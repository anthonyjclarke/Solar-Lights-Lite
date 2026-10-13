// Host regression tests for the scheduler. From firmware/controller/test_host:
//   c++ -std=c++17 -Wall -Wextra -Werror -I../include regression.cpp -o regression && ./regression
#include <cassert>
#include <cstdio>
#include "schedule.h"
using namespace lite;

// Short confirmation and a 5% night level keep the arithmetic easy to follow.
static Scheduler base() {
  Scheduler s;
  s.cfg.selfTestS = 0; s.cfg.confirmS = 5; s.cfg.nightPct = 5;
  return s;
}
static void run(Scheduler& s, int seconds, float v, bool dark, bool light) {
  for (int i = 0; i < seconds; i++) s.step(1, v, dark, light);
}

int main() {
  { // dusk needs uninterrupted darkness for the full confirmation time
    auto s = base();
    for (int i = 0; i < 4; i++) assert(s.step(1, 3.8f, true, false) == 0);
    s.step(1, 3.8f, false, false); assert(!s.night && s.confirm == 0);
    run(s, 5, 3.8f, true, false); assert(s.night && s.state == NIGHT);
  }
  { // 14-hour night at the night level, then off after dawn
    auto s = base();
    for (int i = 0; i < 14 * 3600; i++) { uint8_t p = s.step(1, 3.8f, true, false); assert(p <= 5); if (i > 10) assert(p == 5); }
    run(s, 10, 3.8f, false, true); assert(!s.night && s.state == DAY && s.pct == 0);
  }
  { // startup and button tests never exceed the night level
    auto s = base(); s.cfg.selfTestS = 10;
    assert(s.step(1, 3.8f, false, true) <= 5);
    s.button(); assert(s.step(1, 3.8f, false, true) <= 5);
  }
  { // cut-off after the hold time, button lockout, recovery only in daylight
    auto s = base();
    run(s, 20, 3.8f, true, false);
    run(s, 29, 3.2f, true, false); assert(s.state != LVC);
    assert(s.step(1, 3.2f, true, false) == 0 && s.state == LVC);
    s.button(); for (int i = 0; i < 100; i++) assert(s.step(1, 3.8f, true, false) == 0);
    run(s, 5, 3.8f, false, true); assert(s.state == DAY);
  }
  { // no startup flash on a low battery
    auto s = base(); s.cfg.selfTestS = 10; s.button();
    assert(s.step(1, 3.2f, false, true) == 0);
  }
  { // low battery halves the night level
    auto s = base();
    run(s, 20, 3.8f, true, false); run(s, 20, 3.4f, true, false);
    assert(s.pct == 2);
  }
  { // 8-second idle ticks still confirm dusk and cut-off
    auto s = base();
    s.step(8, 3.8f, true, false); assert(s.night);
    for (int i = 0; i < 4; i++) s.step(8, 3.2f, true, false);
    assert(s.state == LVC && s.pct == 0);
  }
  { // fast ticks only while lit, confirming or testing
    auto s = base();
    s.step(8, 3.8f, false, true); assert(!s.needFastTick());
    s.step(1, 3.8f, true, false); assert(s.needFastTick());
  }
  { // overnight dimming: full for the evening, then the overnight level until dawn
    auto s = base(); s.cfg.nightPct = 100; s.cfg.overnightPct = 30; s.cfg.eveningS = 100;
    run(s, 5, 3.8f, true, false); assert(s.night && s.nightT == 0);
    run(s, 90, 3.8f, true, false); assert(s.pct == 100 && !s.overnight());
    run(s, 10, 3.8f, true, false); assert(s.overnight());
    run(s, 40, 3.8f, true, false); assert(s.pct == 30);           // 2 %/s fade, not a step
    run(s, 20, 3.4f, true, false); assert(s.pct == 15);           // low battery still halves
    run(s, 20, 3.8f, true, false); s.button();
    assert(s.step(1, 3.8f, true, false) == 100);                  // button test overrides
    run(s, 61, 3.8f, true, false); run(s, 40, 3.8f, true, false); assert(s.pct == 30);
    run(s, 5, 3.8f, false, true); run(s, 20, 3.8f, false, true); assert(!s.night && s.pct == 0);
  }
  { // a fresh dusk (after a false dawn or a reset) restarts the evening at full level
    auto s = base(); s.cfg.nightPct = 100; s.cfg.overnightPct = 30; s.cfg.eveningS = 100;
    run(s, 5, 3.8f, true, false); run(s, 200, 3.8f, true, false); assert(s.pct == 30);
    run(s, 5, 3.8f, false, true); assert(!s.night);
    run(s, 5, 3.8f, true, false); run(s, 40, 3.8f, true, false);
    assert(s.night && !s.overnight() && s.pct == 100);
  }
  { // LDR hysteresis: noise just above the dark threshold no longer restarts dusk
    LightSense ls; auto s = base(); s.cfg.confirmS = 300;
    const float noisy[] = {0.29f, 0.302f, 0.28f, 0.301f, 0.295f, 0.31f};
    for (int i = 0; i < 300; i++) {
      ls.update(noisy[i % 6]); assert(i == 0 || ls.dark);
      s.step(1, 3.8f, ls.dark, ls.light);
    }
    assert(s.night);                                   // without hysteresis: never
    ls.update(0.329f); assert(ls.dark);
    ls.update(0.331f); assert(!ls.dark && !ls.light);  // released above 33 %
    ls.update(0.61f); assert(ls.light);
    ls.update(0.58f); assert(ls.light);
    ls.update(0.569f); assert(!ls.light);              // released below 57 %
  }
  { // supply averaging: PWM jitter is smoothed, a real drop still reaches the cut-off
    VddAverage va; auto s = base();
    assert(va.update(3.585f) == 3.585f);               // first reading seeds it
    for (int i = 0; i < 200; i++) va.update(i % 2 ? 3.55f : 3.62f);
    assert(va.value > 3.57f && va.value < 3.60f);
    assert(va.update(0.0f) == va.value);               // failed reading ignored
    run(s, 20, 3.8f, true, false);
    int n = 0; while (s.state != LVC && n < 100) { s.step(1, va.update(3.2f), true, false); n++; }
    assert(s.state == LVC && n < 50);                  // ~11 s to average below 3.30 V, then 30 s
  }
  { // shipped defaults from config.h
    Scheduler s; s.cfg.selfTestS = 0;
    assert(s.cfg.confirmS == 300 && s.cfg.nightPct == 100);
    assert(s.cfg.eveningS == 4UL * 3600 && s.cfg.overnightPct == 30);
    assert(LDR_HYSTERESIS == 0.03f && VDD_AVG_READINGS == 8);
    run(s, 300, 3.8f, true, false); assert(s.night);
    run(s, 60, 3.8f, true, false); assert(s.pct == 100);
    run(s, 60, 3.4f, true, false); assert(s.pct == 50);
    run(s, 4 * 3600, 3.8f, true, false); assert(s.overnight() && s.pct == 30);
  }
  puts("PASS: 13 scheduler groups (confirmation, 14 h night, test caps, cut-off and recovery, "
       "low-voltage startup, low-battery dimming, slow ticks, tick rate, overnight dimming, "
       "fresh dusk, LDR hysteresis, supply averaging, shipped defaults)");
}
