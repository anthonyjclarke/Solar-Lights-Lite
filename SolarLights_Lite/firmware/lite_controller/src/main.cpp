/* v0.5 DEVELOPMENT PROPOSAL - see docs/BUILD_GUIDE.md.
 * Default: switched LDR, resistor-limited 100% dusk-to-dawn, hard cap including test.
 * Requires a VERIFIED 8 MHz clock, including a converted 16 MHz Pro Mini.
 * Do not flash an 8 MHz build onto a stock 16 MHz clock configuration.
 * The v0.5 diagnostic image sends its receive-only telemetry UART on D1/TX
 * through the NPN interface; D8 is left open in that test profile.
 * Panel sense and charger CHRG are disconnected in the revised build.
 *
 * 20-Sep-2026: the string is driven straight from D9 through R3, no Q1. Measured
 * string is a 2.56 V drop with no significant dynamic resistance, so
 * I = (VBAT - 2.56 V) / (R3 + approximately 30 ohm pin resistance): 21/15/11 mA at
 * 4.20/3.70/3.40 V with R3 = 47 ohm. Duty is brightness only; the resistor and the
 * pin bound the current. Pin absolute maximum is 40 mA, 20 mA is the working figure.
 */
/* Pin map: VCC=protected battery (regulator removed), GND=OUT-.
 * A1=LDR midpoint; D7=LDR supply; D9=R3 47R->LED string+ (return to GND, no Q1);
 * D1/TX=47k->NPN base for test telemetry; D8 is left open.
 * D2=button to GND. D10/D11 reserved, leave open. A0 unused in revised build.
 * See validation/ for actual test results; no hardware validation claimed.
 */
#include <Arduino.h>
#include <avr/sleep.h>
#include <avr/wdt.h>
#include <avr/power.h>
#include <util/delay.h>
#include "schedule.h"

// ------------------------------------------------------------ settings
#ifndef SENSOR_LDR
#define SENSOR_LDR    1        // 1 = switched LDR on A1; 0 = legacy panel sense, not wired in v0.5
#endif
#ifndef DEBUG_SERIAL
#define DEBUG_SERIAL  1        // 1 = rate-limited event/progress diagnostics at 9600 baud (~1 mA extra)
#endif
#ifndef DEBUG_ACTIVE_REPORT_S
#define DEBUG_ACTIVE_REPORT_S  10  // progress cadence while confirming/testing/cutoff timing
#endif
#ifndef DEBUG_IDLE_REPORT_S
#define DEBUG_IDLE_REPORT_S    60  // stable-state heartbeat; events still print immediately
#endif
#ifndef TIME_SCALE
#define TIME_SCALE    1        // bench testing: 60 makes 1 real second count as 1 minute
#endif
#ifndef NIGHT_DUTY_PCT
#define NIGHT_DUTY_PCT 100     // dusk-to-dawn commanded duty. With R3 fitted this is
                               // brightness only: peak current is set by R3 and the pin
                               // (approximately 15 mA at 3.7 V with 47 ohm), not by duty.
                               // Lower it to trade brightness for run time; it cannot
                               // make an unmeasured string safe.
#endif
const float PANEL_DARK_V  = 1.5;  // panel volts – tune from serial/HA logs
const float PANEL_LIGHT_V = 3.0;
const float LDR_DARK      = 0.30; // A1 ratio with 100k lower resistor
const float LDR_LIGHT     = 0.60;
const float DIV_PANEL     = (1000.0 + 330.0) / 330.0;
const float BANDGAP_V     = 1.10; // calibrate: BANDGAP_V = 1.10 * Vmeter / Vreported

const uint8_t PIN_PWM = 9, PIN_STATUS = 8, PIN_LDR_PWR = 7, PIN_BTN = 2, PIN_ALLNIGHT = 10, PIN_CAP = 11;

lite::Scheduler sched;
volatile bool wdtFired = false, btnPressed = false;
ISR(WDT_vect) { wdtFired = true; }
ISR(PCINT2_vect) { if (!digitalRead(PIN_BTN)) btnPressed = true; }

static uint8_t wdtPeriod = 0xFF;
void wdtSet(bool fast) {
  uint8_t per = fast ? (_BV(WDP2) | _BV(WDP1)) : (_BV(WDP3) | _BV(WDP0));   // 1 s : 8 s
  if (per == wdtPeriod) return;
  wdtPeriod = per;
  cli();
  wdt_reset();
  MCUSR &= ~_BV(WDRF);
  WDTCSR = _BV(WDCE) | _BV(WDE);
  WDTCSR = _BV(WDIE) | per;
  sei();
}

uint16_t adcRaw(uint8_t mux) {
  ADMUX = _BV(REFS0) | mux;                  // AVcc reference
  _delay_ms(3);
  ADCSRA |= _BV(ADSC); while (bit_is_set(ADCSRA, ADSC));
  ADCSRA |= _BV(ADSC); while (bit_is_set(ADCSRA, ADSC));   // second sample
  return ADC;
}
float readVcc()  { uint16_t r = adcRaw(0x0E); return r ? BANDGAP_V * 1023.0 / r : 0; }

void setup() {
  // unused pins as outputs low (no floating inputs)
  for (uint8_t p = 3; p <= 13; p++) if (p != PIN_ALLNIGHT && p != PIN_CAP) { pinMode(p, OUTPUT); digitalWrite(p, LOW); }
  pinMode(PIN_ALLNIGHT, INPUT_PULLUP); pinMode(PIN_CAP, INPUT_PULLUP);
  _delay_ms(5);
  bool allNight = true, cap = true; // v0.5: user requested dusk-to-dawn
  // D10/D11 are reserved; leave jumpers open in this build.
  pinMode(PIN_ALLNIGHT, OUTPUT); digitalWrite(PIN_ALLNIGHT, LOW);   // release pull-ups
  pinMode(PIN_CAP, OUTPUT); digitalWrite(PIN_CAP, LOW);
  sched.cfg.capPct = NIGHT_DUTY_PCT;          // cap still includes startup and button test
  sched.cfg.allNightPct = NIGHT_DUTY_PCT;
  sched.cfg.predawn = false;
  cap = true;
  sched.begin(allNight, cap);

  pinMode(PIN_BTN, INPUT_PULLUP);             // ~0 µA while the button is open
  PCICR |= _BV(PCIE2); PCMSK2 |= _BV(PCINT18);

  DIDR0 = _BV(ADC0D) | _BV(ADC1D);            // no digital buffers on A0/A1
  TCCR1B = (TCCR1B & 0xF8) | 0x02;            // Timer1 /8 -> D9 PWM ≈ 1.96 kHz
  TIMSK0 &= ~_BV(TOIE0);                      // stop millis tick (keeps idle current low)
  power_twi_disable(); power_spi_disable(); power_timer2_disable();
#if DEBUG_SERIAL
  Serial.begin(9600);
  Serial.println(F("SolarLights Lite diagnostics"));
  Serial.println(F("--- one-time field guide ---"));
  Serial.println(F("time=scheduler seconds since reset; vdd=measured controller supply"));
  Serial.println(F("battery=OK/MID/LOW/CRITICAL voltage band (not a state-of-charge estimate)"));
  Serial.println(F("ldr=A1 as % of VCC; raw=ADC 0..1023; ldr_v=calculated A1 volts"));
  Serial.println(F("sense=DARK below 30%, MID from 30..60%, LIGHT above 60%"));
  Serial.println(F("mode=DAY/EVENING/OVERNIGHT/PREDAWN/LVC scheduler state"));
  Serial.println(F("night=YES after confirmed dusk; output=commanded D9 PWM percentage"));
  Serial.println(F("cause=why output is commanded: test/day/night/low-battery/LVC"));
  Serial.println(F("confirm=DUSK or DAWN elapsed/300s; NONE means no transition pending"));
  Serial.println(F("lvc=seconds below 3.30V/30s; button=manual-test seconds remaining"));
  Serial.println(F("next_tick=planned watchdog interval; 1s active or 8s low-power"));
  Serial.println(F("battery thresholds: LOW<3.45V; LVC<3.30V for 30s; resume>3.60V in DAY"));
  Serial.println(F("reporting: immediate events, 10s active progress, 10% fades, 60s stable"));
  Serial.println(F("--- live diagnostics ---"));
#else
  power_usart0_disable();
#endif
  wdtSet(true);
}

// Fixed duty: the full-charge measurement at 100% is the upper current bound.
// No voltage compensation. With direct drive the current already falls with the cell,
// from about 21 mA at 4.20 V to 11 mA at 3.40 V, and that is intended.
void setLights(uint8_t pct) {
  uint8_t duty = (uint16_t)pct * 255U / 100U;
  if (!duty) { digitalWrite(PIN_PWM, LOW); digitalWrite(PIN_STATUS, LOW); return; }
  analogWrite(PIN_PWM, duty);
  digitalWrite(PIN_STATUS, HIGH);
}

#if DEBUG_SERIAL
static const __FlashStringHelper* stateName(lite::State state) {
  switch (state) {
    case lite::DAY:       return F("DAY");
    case lite::EVENING:   return F("EVENING");
    case lite::OVERNIGHT: return F("OVERNIGHT");
    case lite::PREDAWN:   return F("PREDAWN");
    case lite::LVC:       return F("LVC");
    default:              return F("UNKNOWN");
  }
}

static uint8_t senseCode(bool dark, bool light) { return dark ? 0 : (light ? 2 : 1); }
static const __FlashStringHelper* senseName(uint8_t sense) {
  return sense == 0 ? F("DARK") : (sense == 2 ? F("LIGHT") : F("MID"));
}

// The voltage bands describe firmware decisions, not a calibrated state of charge.
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

static const __FlashStringHelper* outputCause(float vdd, uint8_t pct, bool buttonActive) {
  if (sched.state == lite::LVC) return F("LVC_OFF");
  bool startupActive = sched.t < sched.cfg.selfTestS;
  if ((startupActive || buttonActive) && vdd < sched.cfg.lvcOffV) return F("LOW_VOLT_BLOCK");
  if (startupActive) return F("STARTUP_TEST");
  if (buttonActive) return F("BUTTON_TEST");
  if (sched.state == lite::DAY) return pct ? F("FADE_TO_DAY_OFF") : F("DAY_OFF");
  if (sched.allNight) return vdd < sched.cfg.lowBattV ? F("LOW_BATT_NIGHT") : F("ALL_NIGHT");
  if (sched.state == lite::EVENING) return F("EVENING_SCHEDULE");
  if (sched.state == lite::PREDAWN) return F("PREDAWN_SCHEDULE");
  return F("OVERNIGHT_OFF");
}

static void printDebugStatus(float vdd, uint16_t ldrRaw, float ldrRatio,
                             bool dark, bool light, uint8_t pct, bool fast) {
  static bool first = true;
  static uint32_t lastReport = 0;
  static uint8_t lastState = 0xFF, lastSense = 0xFF, lastBand = 0xFF;
  static uint8_t lastReportedPct = 0;
  static bool lastNight = false, lastButton = false, lastOutputOn = false;

  uint8_t sense = senseCode(dark, light);
  uint8_t band = batteryBand(vdd);
  bool buttonActive = sched.buttonUntil && sched.t <= sched.buttonUntil;
  bool outputOn = pct > 0;
  bool progress = sched.debounce > 0 || sched.lvcCount > 0 || buttonActive;
  uint32_t period = progress ? DEBUG_ACTIVE_REPORT_S : DEBUG_IDLE_REPORT_S;
  uint8_t pctDelta = pct > lastReportedPct ? pct - lastReportedPct : lastReportedPct - pct;
  bool event = first || sched.state != lastState || sense != lastSense || band != lastBand ||
               sched.night != lastNight || buttonActive != lastButton || outputOn != lastOutputOn;
  bool fadeProgress = pctDelta >= 10;
  bool heartbeat = (uint32_t)(sched.t - lastReport) >= period;
  if (!event && !fadeProgress && !heartbeat) return;

  Serial.print(F("time=")); Serial.print(sched.t); Serial.print(F("s"));
  Serial.print(F(" vdd=")); Serial.print(vdd, 3); Serial.print(F("V"));
  Serial.print(F(" battery=")); Serial.print(batteryName(band));
  Serial.print(F(" ldr=")); Serial.print(ldrRatio * 100.0f, 1); Serial.print(F("%"));
  Serial.print(F(" raw=")); Serial.print(ldrRaw);
  Serial.print(F(" ldr_v=")); Serial.print(ldrRatio * vdd, 3); Serial.print(F("V"));
  Serial.print(F(" sense=")); Serial.print(senseName(sense));
  Serial.print(F(" mode=")); Serial.print(stateName(sched.state));
  Serial.print(F(" night=")); Serial.print(sched.night ? F("YES") : F("NO"));
  Serial.print(F(" output=")); Serial.print(pct); Serial.print(F("%"));
  Serial.print(F(" cause=")); Serial.print(outputCause(vdd, pct, buttonActive));

  Serial.print(F(" confirm="));
  if (sched.debounce) {
    Serial.print(sched.night ? F("DAWN") : F("DUSK"));
    Serial.print(F(" ")); Serial.print(sched.debounce); Serial.print(F("/"));
    Serial.print(sched.cfg.debounceS); Serial.print(F("s"));
  } else Serial.print(F("NONE"));

  Serial.print(F(" lvc=")); Serial.print(sched.lvcCount); Serial.print(F("/"));
  Serial.print(sched.cfg.lvcHoldS); Serial.print(F("s"));
  Serial.print(F(" button="));
  Serial.print(buttonActive ? sched.buttonUntil - sched.t : 0); Serial.print(F("s"));
  Serial.print(F(" next_tick=")); Serial.print(fast ? 1 : 8); Serial.println(F("s"));
  Serial.flush();

  first = false; lastReport = sched.t; lastState = sched.state; lastSense = sense;
  lastBand = band; lastReportedPct = pct; lastNight = sched.night;
  lastButton = buttonActive; lastOutputOn = outputOn;
}
#endif

void loop() {
  static uint32_t dt = 1;
  // ---- measure
  power_adc_enable(); ADCSRA |= _BV(ADEN);
  float vdd = readVcc();
  bool dark, light;
#if SENSOR_LDR
  digitalWrite(PIN_LDR_PWR, HIGH); _delay_ms(5);
  uint16_t ldrRaw = adcRaw(1);
  float r = ldrRaw / 1023.0;
  digitalWrite(PIN_LDR_PWR, LOW);
  dark = r < LDR_DARK; light = r > LDR_LIGHT;
#else
  float panel = adcRaw(0) * vdd / 1023.0 * DIV_PANEL;
  dark = panel < PANEL_DARK_V; light = panel > PANEL_LIGHT_V;
#endif
  ADCSRA &= ~_BV(ADEN); power_adc_disable();

  if (btnPressed) { btnPressed = false; sched.button(); }
  uint8_t pct = sched.step(dt * TIME_SCALE, vdd, dark, light);
  setLights(pct);
  bool fast = sched.needFastTick();
#if DEBUG_SERIAL
# if SENSOR_LDR
  printDebugStatus(vdd, ldrRaw, r, dark, light, pct, fast);
# else
  // Legacy panel-sense builds retain a compact line; v0.5 uses the detailed LDR path above.
  Serial.print(F("time=")); Serial.print(sched.t); Serial.print(F("s vdd=")); Serial.print(vdd, 3);
  Serial.print(F("V panel=")); Serial.print(panel, 2); Serial.print(F("V mode="));
  Serial.print(stateName(sched.state)); Serial.print(F(" output=")); Serial.print(pct); Serial.println(F("%"));
  Serial.flush();
# endif
#endif

  // ---- sleep until the watchdog (or button)
  wdtSet(fast);
  dt = fast ? 1 : 8;
  wdtFired = false;
  set_sleep_mode(pct ? SLEEP_MODE_IDLE : SLEEP_MODE_PWR_DOWN);   // Timer1 PWM needs IDLE
  cli();
  if (!wdtFired && !btnPressed) {
    sleep_enable();
    if (!pct) sleep_bod_disable();
    sei();
    sleep_cpu();
    sleep_disable();
  }
  sei();
  if (btnPressed && !wdtFired) dt = 1;   // approximate: button woke us early
}
