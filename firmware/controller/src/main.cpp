/*
 * Solar Lights Lite – dusk-to-dawn controller for a low-power LED string
 * ---------------------------------------------------------------------
 * Target: ATmega328P Pro Mini-class board on its internal 8 MHz oscillator
 * (fuses L 0xE2, H 0xD9, E 0xFD: no bootloader, 2.7 V brown-out), powered
 * directly from the protected 1S Li-ion rail with the board regulator removed.
 * Firmware is flashed over ISP; see docs/08-firmware.md.
 *
 * Each watchdog wake measures the supply against the internal bandgap, briefly
 * powers the LDR divider and reads A1, advances the scheduler (schedule.h),
 * sets the D9 PWM duty and goes back to sleep.
 *
 * Lighting: D9 drives a LOW-POWER LED string directly by PWM through R3
 * (47 ohm). There is no driver transistor. R3 and the pin's own resistance set
 * the current; duty sets brightness only. The pin's 20 mA working rating is the
 * design ceiling, so this output cannot run mains, 12 V or conventional lights.
 *
 * Telemetry, selected by the TELEMETRY build flag (one PlatformIO environment each):
 *   0  standalone  no serial output; USART powered down
 *   1  production  banner at reset, then one compact line every STATUS_INTERVAL_S;
 *                  USART on only while sending
 *   2  advanced    banner and field guide at reset, then full diagnostics; USART always on
 * Lines are space-separated key=value pairs at 9600 baud on D1/TX, starting
 * with fw=. The D1 Mini receives them through the Q2 inverter, and both
 * ESPHome profiles parse the same keys: rename a key here, update both YAML files.
 */
#include <Arduino.h>
#include <avr/sleep.h>
#include <avr/wdt.h>
#include <avr/power.h>
#include <util/delay.h>
#include "config.h"
#include "schedule.h"

#ifndef TELEMETRY
#define TELEMETRY 1
#endif

struct Reading {
  float    vdd;       // controller supply, volts
  uint16_t ldrRaw;    // A1, 0..1023
  float    ldrRatio;  // A1 as a fraction of VCC
  bool     dark, light;
};

lite::Scheduler sched;
volatile bool wdtFired = false, btnPressed = false;
ISR(WDT_vect) { wdtFired = true; }
ISR(PCINT2_vect) { if (!digitalRead(PIN_BUTTON)) btnPressed = true; }

// ------------------------------------------------------------ hardware helpers
static uint8_t wdtPeriod = 0xFF;
static void wdtSet(bool fast) {
  uint8_t per = fast ? (_BV(WDP2) | _BV(WDP1)) : (_BV(WDP3) | _BV(WDP0));   // 1 s : 8 s
  if (per == wdtPeriod) return;
  wdtPeriod = per;
  cli();
  wdt_reset();
  MCUSR &= ~_BV(WDRF);
  WDTCSR = _BV(WDCE) | _BV(WDE);
  WDTCSR = _BV(WDIE) | per;                  // interrupt only, never a reset
  sei();
}

static uint16_t adcRaw(uint8_t mux) {
  ADMUX = _BV(REFS0) | mux;                  // AVcc reference
  _delay_ms(3);
  ADCSRA |= _BV(ADSC); while (bit_is_set(ADCSRA, ADSC));
  ADCSRA |= _BV(ADSC); while (bit_is_set(ADCSRA, ADSC));   // keep the settled second sample
  return ADC;
}

// VCC from the 1.1 V bandgap measured against AVcc (mux 0x0E)
static float readVcc() { uint16_t r = adcRaw(0x0E); return r ? BANDGAP_V * 1023.0f / r : 0; }

static Reading measure() {
  Reading r;
  power_adc_enable(); ADCSRA |= _BV(ADEN);
  r.vdd = readVcc();
  digitalWrite(PIN_LDR_PWR, HIGH); _delay_ms(5);   // LDR divider draws current only now
  r.ldrRaw = adcRaw(ADC_LDR);
  digitalWrite(PIN_LDR_PWR, LOW);
  ADCSRA &= ~_BV(ADEN); power_adc_disable();
  r.ldrRatio = r.ldrRaw / 1023.0f;
  r.dark = r.ldrRatio < LDR_DARK_RATIO;
  r.light = r.ldrRatio > LDR_LIGHT_RATIO;
  return r;
}

// Fixed duty, no voltage compensation: with direct drive the LED current
// already falls with the cell voltage, and that is intended.
static void setLights(uint8_t pct) {
  uint8_t duty = (uint16_t)pct * 255U / 100U;
  if (!duty) digitalWrite(PIN_LED_PWM, LOW);
  else analogWrite(PIN_LED_PWM, duty);
}

#if TELEMETRY != 2
// Hold D1/TX low between transmissions: Q2 stays off, so the link draws nothing
// and the pin never floats (the USART takes the pin over again when enabled).
static void releaseTx() { pinMode(PIN_TX, OUTPUT); digitalWrite(PIN_TX, LOW); }
#endif

// ------------------------------------------------------------ telemetry text
#if TELEMETRY
static const __FlashStringHelper* stateName(lite::State s) {
  switch (s) {
    case lite::DAY:   return F("DAY");
    case lite::NIGHT: return F("NIGHT");
    case lite::LVC:   return F("LVC");
    default:          return F("UNKNOWN");
  }
}

static const __FlashStringHelper* senseName(const Reading& r) {
  return r.dark ? F("DARK") : (r.light ? F("LIGHT") : F("MID"));
}

// Voltage bands describe firmware decisions, not a calibrated state of charge.
static uint8_t batteryBand(float vdd) {
  if (vdd < sched.cfg.lvcOffV) return 0;
  if (vdd < sched.cfg.lowBattV) return 1;
  if (vdd <= sched.cfg.lvcResumeV) return 2;
  return 3;
}
static const __FlashStringHelper* batteryName(uint8_t band) {
  switch (band) {
    case 0:  return F("CRITICAL");
    case 1:  return F("LOW");
    case 2:  return F("MID");
    default: return F("OK");
  }
}

static const __FlashStringHelper* outputCause(float vdd, uint8_t pct) {
  if (sched.state == lite::LVC) return F("LVC_OFF");
  bool startup = sched.t < sched.cfg.selfTestS;
  bool button = sched.buttonActive();
  if ((startup || button) && vdd < sched.cfg.lvcOffV) return F("LOW_VOLT_BLOCK");
  if (startup) return F("STARTUP_TEST");
  if (button) return F("BUTTON_TEST");
  if (sched.state == lite::DAY) return pct ? F("FADE_TO_DAY_OFF") : F("DAY_OFF");
  return vdd < sched.cfg.lowBattV ? F("LOW_BATT_NIGHT") : F("DUSK_TO_DAWN");
}

// One telemetry line. Production sends the core keys; advanced adds progress detail.
static void printLine(bool full, const Reading& r, uint8_t pct, bool fast) {
  Serial.print(F("fw=")); Serial.print(FW_VERSION);
  Serial.print(F(" time=")); Serial.print(sched.t); Serial.print(F("s"));
  Serial.print(F(" vdd=")); Serial.print(r.vdd, 3); Serial.print(F("V"));
  Serial.print(F(" battery=")); Serial.print(batteryName(batteryBand(r.vdd)));
  Serial.print(F(" ldr=")); Serial.print(r.ldrRatio * 100.0f, 1); Serial.print(F("%"));
  Serial.print(F(" sense=")); Serial.print(senseName(r));
  Serial.print(F(" mode=")); Serial.print(stateName(sched.state));
  Serial.print(F(" night=")); Serial.print(sched.night ? F("YES") : F("NO"));
  Serial.print(F(" output=")); Serial.print(pct); Serial.print(F("%"));
  Serial.print(F(" cause=")); Serial.print(outputCause(r.vdd, pct));
  if (full) {
    Serial.print(F(" raw=")); Serial.print(r.ldrRaw);
    Serial.print(F(" ldr_v=")); Serial.print(r.ldrRatio * r.vdd, 3); Serial.print(F("V"));
    Serial.print(F(" confirm="));
    if (sched.confirm) {
      Serial.print(sched.night ? F("DAWN") : F("DUSK"));
      Serial.print(F(" ")); Serial.print(sched.confirm); Serial.print(F("/"));
      Serial.print(sched.cfg.confirmS); Serial.print(F("s"));
    } else Serial.print(F("NONE"));
    Serial.print(F(" lvc=")); Serial.print(sched.lvcCount); Serial.print(F("/"));
    Serial.print(sched.cfg.lvcHoldS); Serial.print(F("s"));
    Serial.print(F(" button="));
    Serial.print(sched.buttonActive() ? sched.buttonUntil - sched.t : 0); Serial.print(F("s"));
    Serial.print(F(" next_tick=")); Serial.print(fast ? 1 : 8); Serial.print(F("s"));
  }
  Serial.println();
}
#endif

#if TELEMETRY
// __DATE__ is "Mmm dd yyyy" with a space-padded day; printed as dd-Mmm-yyyy hh:mm.
static void printBuildStamp() {
  const char* d = __DATE__;
  Serial.print(d[4] == ' ' ? '0' : d[4]); Serial.print(d[5]); Serial.print('-');
  Serial.write(d, 3); Serial.print('-'); Serial.write(d + 7, 4);
  Serial.print(' '); Serial.write(__TIME__, 5);
}

// Reset banner. No line starts with fw=, so both ESPHome profiles ignore it.
static void printBanner() {
  Serial.println();
  Serial.println(F("=================================================="));
  Serial.println(F(" Solar Lights Lite  -  dusk-to-dawn controller"));
  Serial.print(F(" Firmware   v")); Serial.print(FW_VERSION);
  Serial.print(F("   built ")); printBuildStamp(); Serial.println();
#if TELEMETRY == 2
  Serial.println(F(" Telemetry  advanced: full diagnostics, 9600 baud"));
#else
  Serial.println(F(" Telemetry  production: compact line, 9600 baud"));
#endif
  Serial.println(F(" Clock      internal 8 MHz, brown-out 2.7 V"));
  Serial.println(F("=================================================="));
}
#endif

#if TELEMETRY == 2
static void printFieldGuide() {
  Serial.println(F("Settings"));
  Serial.print(F("  LDR        dark <")); Serial.print(LDR_DARK_RATIO * 100.0f, 0);
  Serial.print(F("%  light >")); Serial.print(LDR_LIGHT_RATIO * 100.0f, 0);
  Serial.print(F("%  confirm ")); Serial.print(TRANSITION_CONFIRM_S); Serial.println(F(" s"));
  Serial.print(F("  Battery    low <")); Serial.print(LOW_BATT_V, 2);
  Serial.println(F(" V halves night duty"));
  Serial.print(F("             cut-off <")); Serial.print(LVC_OFF_V, 2);
  Serial.print(F(" V for ")); Serial.print(LVC_HOLD_S);
  Serial.print(F(" s, resume >")); Serial.print(LVC_RESUME_V, 2); Serial.println(F(" V in daylight"));
  Serial.print(F("  Duty       night ")); Serial.print(NIGHT_DUTY_PCT);
  Serial.print(F("%  button test ")); Serial.print(BUTTON_TEST_S); Serial.println(F(" s"));
  Serial.println(F("Field guide (keys in each line)"));
  Serial.println(F("  time       scheduler seconds since reset (watchdog clock, not wall-clock)"));
  Serial.println(F("  vdd        controller supply; battery = OK/MID/LOW/CRITICAL band"));
  Serial.println(F("  ldr        A1 as % of VCC; raw = ADC 0-1023; ldr_v = A1 volts"));
  Serial.println(F("  sense      DARK / MID / LIGHT from the LDR thresholds above"));
  Serial.println(F("  mode       DAY / NIGHT / LVC; night = YES after a confirmed dusk"));
  Serial.println(F("  output     D9 PWM duty; cause = why output has that value"));
  Serial.println(F("  confirm    DUSK or DAWN progress, NONE when idle"));
  Serial.println(F("  lvc        seconds below cut-off; button = test seconds left"));
  Serial.println(F("  next_tick  1 s while active, 8 s when idle"));
  Serial.println(F("--------------------------------------------------"));
  Serial.println(F("Live diagnostics"));
}
#endif

// Advanced: report events immediately, progress every ADVANCED_ACTIVE_REPORT_S,
// fades at 10-point steps and a heartbeat every ADVANCED_IDLE_REPORT_S.
// Production: one compact line every STATUS_INTERVAL_S. Standalone: nothing.
static void report(const Reading& r, uint8_t pct, bool fast) {
#if TELEMETRY == 1
  static bool first = true;
  static uint32_t last = 0;
  if (!first && (uint32_t)(sched.t - last) < STATUS_INTERVAL_S) return;
  first = false; last = sched.t;
  power_usart0_enable();
  Serial.begin(9600);
  printLine(false, r, pct, fast);
  Serial.flush();
  Serial.end();
  power_usart0_disable();
  releaseTx();
#elif TELEMETRY == 2
  static bool first = true;
  static uint32_t last = 0;
  static uint8_t lastState = 0xFF, lastSense = 0xFF, lastBand = 0xFF, lastPct = 0;
  static bool lastNight = false, lastButton = false;
  uint8_t sense = r.dark ? 0 : (r.light ? 2 : 1);
  uint8_t band = batteryBand(r.vdd);
  bool button = sched.buttonActive();
  bool progress = sched.confirm > 0 || sched.lvcCount > 0 || button;
  uint32_t period = progress ? ADVANCED_ACTIVE_REPORT_S : ADVANCED_IDLE_REPORT_S;
  uint8_t pctDelta = pct > lastPct ? pct - lastPct : lastPct - pct;
  bool event = first || sched.state != lastState || sense != lastSense || band != lastBand ||
               sched.night != lastNight || button != lastButton || (pct > 0) != (lastPct > 0);
  bool heartbeat = (uint32_t)(sched.t - last) >= period;
  if (!event && pctDelta < 10 && !heartbeat) return;
  printLine(true, r, pct, fast);
  Serial.flush();
  first = false; last = sched.t; lastState = sched.state; lastSense = sense;
  lastBand = band; lastPct = pct; lastNight = sched.night; lastButton = button;
#else
  (void)r; (void)pct; (void)fast;
#endif
}

// ------------------------------------------------------------ setup
static void initPins() {
  // Unused digital pins are driven low so nothing floats during sleep.
  for (uint8_t p = 3; p <= 13; p++) { pinMode(p, OUTPUT); digitalWrite(p, LOW); }
  pinMode(0, INPUT_PULLUP);                  // RX is never used
  pinMode(PIN_BUTTON, INPUT_PULLUP);         // ~0 uA while the button is open
  PCICR |= _BV(PCIE2); PCMSK2 |= _BV(PCINT18);   // D2 wakes the controller
  DIDR0 = 0x3F;                              // no digital input buffers on A0-A5
}

static void initPower() {
  TCCR1B = (TCCR1B & 0xF8) | 0x02;           // Timer1 /8 -> D9 PWM ~1.96 kHz
  TIMSK0 &= ~_BV(TOIE0);                     // stop the millis() tick; keeps idle current low
  power_twi_disable(); power_spi_disable(); power_timer2_disable();
}

static void initTelemetry() {
#if TELEMETRY == 2
  Serial.begin(9600);
  printBanner();
  printFieldGuide();
#elif TELEMETRY == 1
  Serial.begin(9600);
  printBanner();
  Serial.flush();
  Serial.end();
  power_usart0_disable();
  releaseTx();
#else
  power_usart0_disable();
  releaseTx();
#endif
}

void setup() {
  initPins();
  initPower();
  initTelemetry();
  wdtSet(true);
}

// ------------------------------------------------------------ loop
// Sleep until the watchdog or the button; returns the scheduler seconds elapsed.
static uint32_t sleepUntilWake(bool fast, bool lit) {
  wdtSet(fast);
  wdtFired = false;
  set_sleep_mode(lit ? SLEEP_MODE_IDLE : SLEEP_MODE_PWR_DOWN);   // Timer1 PWM needs IDLE
  cli();
  if (!wdtFired && !btnPressed) {
    sleep_enable();
    if (!lit) sleep_bod_disable();
    sei();
    sleep_cpu();
    sleep_disable();
  }
  sei();
  if (btnPressed && !wdtFired) return 1;     // approximate: the button woke us early
  return fast ? 1 : 8;
}

void loop() {
  static uint32_t dt = 1;
  Reading r = measure();
  if (btnPressed) { btnPressed = false; sched.button(); }
  uint8_t pct = sched.step(dt * TIME_SCALE, r.vdd, r.dark, r.light);
  setLights(pct);
  bool fast = sched.needFastTick();
  report(r, pct, fast);
  dt = sleepUntilWake(fast, pct > 0);
}
