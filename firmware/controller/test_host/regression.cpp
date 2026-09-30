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
  { // shipped defaults from config.h
    Scheduler s; s.cfg.selfTestS = 0;
    assert(s.cfg.confirmS == 300 && s.cfg.nightPct == 100);
    run(s, 300, 3.8f, true, false); assert(s.night);
    run(s, 60, 3.8f, true, false); assert(s.pct == 100);
    run(s, 60, 3.4f, true, false); assert(s.pct == 50);
  }
  puts("PASS: 9 scheduler groups (confirmation, 14 h night, test caps, cut-off and recovery, "
       "low-voltage startup, low-battery dimming, slow ticks, tick rate, shipped defaults)");
}
