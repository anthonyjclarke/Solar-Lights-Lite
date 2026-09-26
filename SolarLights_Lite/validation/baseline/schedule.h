/*
 * SolarLights Lite – hardware-independent scheduler
 * -------------------------------------------------
 * Same behaviour as the v2 ATtiny controller, packaged so it can be unit-tested
 * on a Mac/PC (see test_host/). No Arduino or AVR headers in here.
 *
 * Call step() after every wake with the seconds elapsed since the last call.
 */
#pragma once
#include <stdint.h>

namespace lite {

// ------------------------------------------------------------ tunables
struct Config {
  uint16_t debounceS          = 300;          // dusk/dawn must persist 5 min
  uint32_t eveningEndBeforeMid = 90UL * 60;   // lights down ~22:25 AEST
  uint32_t morningStartAfterMid = 330UL * 60; // pre-dawn from ~05:25 AEST
  uint32_t minEveningS        = 2UL * 3600;
  uint32_t fallbackEveningS   = 5UL * 3600;   // first night, before learning
  uint32_t nightMinS          = 6UL * 3600;
  uint32_t nightMaxS          = 16UL * 3600;
  uint8_t  allNightPct        = 10;           // MODE jumper "all night"
  uint8_t  capPct             = 30;           // MODE jumper "low brightness"
  bool     predawn            = true;         // false = evening window only (Stage 1 panel)
  uint8_t  lowBattPct         = 8;
  uint8_t  selfTestPct        = 20;
  uint16_t selfTestS          = 10;
  uint8_t  buttonPct          = 30;
  uint16_t buttonS            = 60;
  float    lvcOffV            = 3.30f;
  float    lvcResumeV         = 3.60f;
  float    lowBattV           = 3.45f;
  uint16_t lvcHoldS           = 30;
  uint8_t  fadeStepPct        = 2;            // % per second
};

enum State : uint8_t { DAY = 0, EVENING = 1, OVERNIGHT = 2, PREDAWN = 3, LVC = 4 };

inline uint8_t eveningPctFor(float v, bool cap, const Config& c) {
  uint8_t p = v >= 3.95f ? 60 : v >= 3.80f ? 45 : v >= 3.65f ? 30 : v >= 3.50f ? 15 : c.lowBattPct;
  if (cap && p > c.capPct) p = c.capPct;
  return p;
}

class Scheduler {
public:
  Config cfg;
  State    state = DAY;
  bool     night = false, learned = false, allNight = false, lowCap = false;
  uint32_t t = 0;                 // seconds since boot (WDT clock)
  uint32_t nightLen = 0, duskAt = 0, eveningEnd = 0, morningStart = 0xFFFFFFFFUL;
  uint8_t  eveningPct = 0, pct = 0;
  uint32_t debounce = 0, lvcCount = 0, buttonUntil = 0;

  void begin(bool allNightJumper, bool lowCapJumper) { allNight = allNightJumper; lowCap = lowCapJumper; }
  void button() { buttonUntil = t + cfg.buttonS; }

  // dark/light: sensor says clearly dark / clearly light (between thresholds both false)
  uint8_t step(uint32_t dt, float vdd, bool dark, bool light) {
    t += dt;
    // ---- dusk/dawn debounce
    bool cand = night ? light : dark;
    debounce = cand ? debounce + dt : 0;
    if (debounce >= cfg.debounceS) {
      debounce = 0;
      night = !night;
      uint32_t at = t - cfg.debounceS;
      if (night) onDusk(at, vdd); else onDawn(at);
    }
    // ---- battery cut-off
    lvcCount = (vdd < cfg.lvcOffV) ? lvcCount + dt : 0;
    if (state != LVC && lvcCount >= cfg.lvcHoldS) state = LVC;
    if (state == LVC && vdd > cfg.lvcResumeV && !night) state = DAY;
    if (state != LVC) {
      if (!night)                 state = DAY;
      else if (t < eveningEnd)    state = EVENING;
      else if (t >= morningStart) state = PREDAWN;
      else                        state = OVERNIGHT;
    }
    // ---- target + fade
    uint8_t tgt = target(vdd);
    bool instant = (t <= cfg.selfTestS) || (buttonUntil && t <= buttonUntil);
    uint32_t step = instant ? 100 : (uint32_t)cfg.fadeStepPct * dt;
    if (pct < tgt)      pct = ((uint32_t)(tgt - pct) > step) ? (uint8_t)(pct + step) : tgt;
    else if (pct > tgt) pct = ((uint32_t)(pct - tgt) > step) ? (uint8_t)(pct - step) : tgt;
    return pct;
  }

  // true while the controller should wake every second (lit, fading, or confirming dusk/dawn)
  bool needFastTick() const { return pct > 0 || debounce > 0 || t < cfg.selfTestS || (buttonUntil && t < buttonUntil); }

private:
  uint8_t target(float vdd) const {
    if (t < cfg.selfTestS) return cfg.selfTestPct;
    if (buttonUntil && t <= buttonUntil && state != LVC) return cfg.buttonPct;
    if (state == LVC || state == DAY) return 0;
    bool low = vdd < cfg.lowBattV;
    switch (state) {
      case EVENING:   return (low && eveningPct > cfg.lowBattPct) ? cfg.lowBattPct : eveningPct;
      case PREDAWN:   return low ? 0 : eveningPct;
      case OVERNIGHT: return allNight ? (low ? cfg.lowBattPct / 2 : cfg.allNightPct) : 0;
      default:        return 0;
    }
  }
  void onDusk(uint32_t at, float vdd) {
    duskAt = at;
    eveningPct = eveningPctFor(vdd, lowCap, cfg);
    if (learned) {
      uint32_t mid = duskAt + nightLen / 2;
      eveningEnd = mid - cfg.eveningEndBeforeMid;
      if (eveningEnd < duskAt + cfg.minEveningS) eveningEnd = duskAt + cfg.minEveningS;
      morningStart = cfg.predawn ? mid + cfg.morningStartAfterMid : 0xFFFFFFFFUL;
    } else {
      eveningEnd = duskAt + cfg.fallbackEveningS;
      morningStart = 0xFFFFFFFFUL;
    }
  }
  void onDawn(uint32_t at) {
    uint32_t len = at - duskAt;
    if (len > cfg.nightMinS && len < cfg.nightMaxS) { nightLen = len; learned = true; }
  }
};

} // namespace lite
