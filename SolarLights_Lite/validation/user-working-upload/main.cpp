/* REV 0.4 REVIEW PROPOSAL - see docs/BUILD_GUIDE.md.
 * Default: switched LDR, uniform 5% dusk-to-dawn, hard cap including test.
 * Requires a VERIFIED 8 MHz clock, including a converted 16 MHz Pro Mini.
 * Do not flash an 8 MHz build onto a stock 16 MHz clock configuration.
 * D8 status uses an NPN inverter in the revised wiring (not the old divider).
 * Panel sense and charger CHRG are disconnected in the revised build.
 */
/* Pin map: VCC=protected battery (regulator removed), GND=OUT-.
 * A1=LDR midpoint; D7=LDR supply; D9=100R->Q1 gate; D8=47k->NPN base.
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
#define SENSOR_LDR    1        // 1 = switched LDR on A1; 0 = legacy panel sense, not wired in Rev 0.4
#endif
#ifndef DEBUG_SERIAL
#define DEBUG_SERIAL  1        // 1 = print one status line per wake at 9600 baud (bench only – uses ~1 mA more)
#endif
#ifndef TIME_SCALE
#define TIME_SCALE    1        // bench testing: 60 makes 1 real second count as 1 minute
#endif
#ifndef PANEL_STAGE
#define PANEL_STAGE   1        // 1 = existing panel, fixed 5% dusk-to-dawn
                               // 2 = optional 10% profile ONLY after measured energy budget passes
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
  bool allNight = true, cap = true; // Rev 0.4: user requested dusk-to-dawn
  // D10/D11 are reserved; leave jumpers open in this build.
  pinMode(PIN_ALLNIGHT, OUTPUT); digitalWrite(PIN_ALLNIGHT, LOW);   // release pull-ups
  pinMode(PIN_CAP, OUTPUT); digitalWrite(PIN_CAP, LOW);
#if PANEL_STAGE == 1
  sched.cfg.capPct = 5;
  sched.cfg.allNightPct = 5;
  sched.cfg.predawn = false;
  cap = true;                                 // hard duty cap includes startup/test
#else
  sched.cfg.capPct = 10;
  sched.cfg.allNightPct = 10;
  sched.cfg.predawn = false;
#endif
  sched.begin(allNight, cap);

  pinMode(PIN_BTN, INPUT_PULLUP);             // ~0 µA while the button is open
  PCICR |= _BV(PCIE2); PCMSK2 |= _BV(PCINT18);

  DIDR0 = _BV(ADC0D) | _BV(ADC1D);            // no digital buffers on A0/A1
  TCCR1B = (TCCR1B & 0xF8) | 0x02;            // Timer1 /8 -> D9 PWM ≈ 1.96 kHz
  TIMSK0 &= ~_BV(TOIE0);                      // stop millis tick (keeps idle current low)
  power_twi_disable(); power_spi_disable(); power_timer2_disable();
#if DEBUG_SERIAL
  Serial.begin(19200);
  Serial.println(F("SolarLights Lite"));
#else
  power_usart0_disable();
#endif
  wdtSet(true);
}

// Fixed duty makes the full-charge peak-current measurement an upper budget bound.
// No voltage compensation: 5% must never silently become 10% at low battery.
void setLights(uint8_t pct) {
  uint8_t duty = (uint16_t)pct * 255U / 100U;
  if (!duty) { digitalWrite(PIN_PWM, LOW); digitalWrite(PIN_STATUS, LOW); return; }
  analogWrite(PIN_PWM, duty);
  digitalWrite(PIN_STATUS, HIGH);
}

void loop() {
  static uint32_t dt = 1;
  // ---- measure
  power_adc_enable(); ADCSRA |= _BV(ADEN);
  float vdd = readVcc();
  bool dark, light;
#if SENSOR_LDR
  digitalWrite(PIN_LDR_PWR, HIGH); _delay_ms(5);
  float r = adcRaw(1) / 1023.0;
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
#if DEBUG_SERIAL
  Serial.print(F("t=")); Serial.print(sched.t); Serial.print(F(" vdd=")); Serial.print(vdd, 3);
# if !SENSOR_LDR
  Serial.print(F(" panel=")); Serial.print(panel, 2);
# endif
  Serial.print(F(" state=")); Serial.print(sched.state); Serial.print(F(" pct=")); Serial.println(pct);
  Serial.flush();
#endif

  // ---- sleep until the watchdog (or button)
  bool fast = sched.needFastTick();
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
