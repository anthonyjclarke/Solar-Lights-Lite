/*
 * Solar Lights Lite – hardware-independent scheduler
 * --------------------------------------------------
 * Dusk-to-dawn lighting with confirmed transitions, low-battery dimming,
 * low-voltage cut-off, a startup self-test and a timed button test. No Arduino
 * or AVR headers, so the host regression tests in test_host/ run this exact code.
 *
 * Call step() after every wake with the scheduler seconds elapsed since the last call.
 */
#pragma once
#include <stdint.h>
#include "config.h"

namespace lite {

struct Config {
  uint16_t confirmS    = TRANSITION_CONFIRM_S;
  uint8_t  nightPct    = NIGHT_DUTY_PCT;  // also caps the startup and button tests
  uint8_t  selfTestPct = STARTUP_TEST_PCT;
  uint16_t selfTestS   = STARTUP_TEST_S;
  uint8_t  buttonPct   = BUTTON_TEST_PCT;
  uint16_t buttonS     = BUTTON_TEST_S;
  float    lowBattV    = LOW_BATT_V;
  float    lvcOffV     = LVC_OFF_V;
  uint16_t lvcHoldS    = LVC_HOLD_S;
  float    lvcResumeV  = LVC_RESUME_V;
  uint8_t  fadeStepPct = FADE_STEP_PCT;
};

enum State : uint8_t { DAY = 0, NIGHT = 1, LVC = 2 };

class Scheduler {
public:
  Config   cfg;
  State    state = DAY;
  bool     night = false;    // dusk confirmed and dawn not yet confirmed
  uint32_t t = 0;            // scheduler seconds since reset (watchdog clock)
  uint8_t  pct = 0;          // output duty, %
  uint32_t confirm = 0;      // seconds the opposite light level has persisted
  uint32_t lvcCount = 0;     // seconds below the cut-off voltage
  uint32_t buttonUntil = 0;

  void button() { buttonUntil = t + cfg.buttonS; }
  bool buttonActive() const { return buttonUntil && t <= buttonUntil; }

  // dark / light: the sensor is clearly dark / clearly light (both false in between)
  uint8_t step(uint32_t dt, float vdd, bool dark, bool light) {
    t += dt;
    // ---- dusk/dawn only after the new light level persists
    bool candidate = night ? light : dark;
    confirm = candidate ? confirm + dt : 0;
    if (confirm >= cfg.confirmS) { confirm = 0; night = !night; }
    // ---- low-voltage cut-off: latches until daylight and recovery voltage
    lvcCount = (vdd < cfg.lvcOffV) ? lvcCount + dt : 0;
    if (state != LVC && lvcCount >= cfg.lvcHoldS) state = LVC;
    if (state == LVC && vdd > cfg.lvcResumeV && !night) state = DAY;
    if (state != LVC) state = night ? NIGHT : DAY;
    if (state == LVC) { pct = 0; return 0; }  // protection must not fade out
    // ---- target, capped at the night level, then fade towards it
    uint8_t tgt = target(vdd);
    if (tgt > cfg.nightPct) tgt = cfg.nightPct;
    bool instant = (t <= cfg.selfTestS) || buttonActive();
    uint32_t stepPct = instant ? 100 : (uint32_t)cfg.fadeStepPct * dt;
    if (pct < tgt)      pct = ((uint32_t)(tgt - pct) > stepPct) ? (uint8_t)(pct + stepPct) : tgt;
    else if (pct > tgt) pct = ((uint32_t)(pct - tgt) > stepPct) ? (uint8_t)(pct - stepPct) : tgt;
    return pct;
  }

  // true while the controller should wake every second (lit, fading, confirming or testing)
  bool needFastTick() const {
    return pct > 0 || confirm > 0 || t < cfg.selfTestS || (buttonUntil && t < buttonUntil);
  }

private:
  uint8_t target(float vdd) const {
    if (t < cfg.selfTestS) return vdd >= cfg.lvcOffV ? cfg.selfTestPct : 0;
    if (buttonActive() && vdd >= cfg.lvcOffV) return cfg.buttonPct;
    if (state == DAY) return 0;
    return vdd < cfg.lowBattV ? cfg.nightPct / 2 : cfg.nightPct;
  }
};

} // namespace lite
