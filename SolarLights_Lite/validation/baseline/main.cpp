/*
 * SolarLights Lite – Arduino Pro Mini 3.3 V / 8 MHz controller
 * ============================================================
 * Parts-bin version of the v2 controller. Runs the LED string on its own;
 * the Wemos D1 Mini only reports to Home Assistant.
 *
 * Board prep: remove the power LED (or its resistor) and the 3.3 V regulator;
 * feed the battery (TP4056 OUT+) to VCC, not RAW.
 *
 * Pin map
 *   VCC  <- TP4056 OUT+ (3.0–4.2 V)      GND <- TP4056 OUT−
 *   A0   <- panel sense: PV+ (before diodes) -> 1M -> A0 -> 330k -> GND, 100 nF
 *   A1   <- LDR option:  D7 -> LDR -> A1 -> 100k -> GND   (set SENSOR_LDR 1)
 *   D7   -> LDR divider power (high only while sampling)
 *   D9   -> 100 Ω -> MOSFET gate (100k gate->GND). D9 = Timer1 PWM ~2 kHz
 *   D8   -> LIGHTS_ON -> 100k -> D1 Mini D5 (220k D5->GND)
 *   D2   <- push button to GND: lights 30 % for 60 s (install/test)
 *   D10  <- jumper to GND at boot: all-night 10 % mode
 *   D11  <- jumper to GND at boot: brightness cap 30 %
 *
 * Status: compiles (avr-gcc, Arduino AVR core 1.8.6); scheduler host-tested.
 *         Not yet run on hardware – bench-test before installing.
 */
#include <Arduino.h>
#include <avr/sleep.h>
#include <avr/wdt.h>
#include <avr/power.h>
#include <util/delay.h>
#include "schedule.h"

// ------------------------------------------------------------ settings
#define SENSOR_LDR    0        // 0 = panel voltage on A0 (recommended), 1 = LDR on A1
#define DEBUG_SERIAL  0        // 1 = print one status line per wake at 9600 baud (bench only – uses ~1 mA more)
#define TIME_SCALE    1        // bench testing: 60 makes 1 real second count as 1 minute
#define PANEL_STAGE   1        // 1 = existing 1.2 W panel: brightness cap 20 %, no pre-dawn
                               // 2 = 6 V 5 W panel: full levels (D11 jumper = 30 % cap), pre-dawn on
const float PANEL_DARK_V  = 1.5;  // panel volts – tune from serial/HA logs
const float PANEL_LIGHT_V = 3.0;
const float LDR_DARK      = 0.30; // A1 ratio with 100k lower resistor
const float LDR_LIGHT     = 0.60;
const float DIV_PANEL     = (1000.0 + 330.0) / 330.0;
const float BANDGAP_V     = 1.10; // calibrate: BANDGAP_V = 1.10 * Vmeter / Vreported
const float LED_VF        = 2.9;  // droop compensation (measure your string)
const float COMP_REF_V    = 3.8;

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
  bool allNight = !digitalRead(PIN_ALLNIGHT), cap = !digitalRead(PIN_CAP);
  pinMode(PIN_ALLNIGHT, OUTPUT); digitalWrite(PIN_ALLNIGHT, LOW);   // release pull-ups
  pinMode(PIN_CAP, OUTPUT); digitalWrite(PIN_CAP, LOW);
#if PANEL_STAGE == 1
  sched.cfg.capPct = 20;
  sched.cfg.predawn = false;
  cap = true;                                 // cap always applies on the small panel
#endif
  sched.begin(allNight, cap);

  pinMode(PIN_BTN, INPUT_PULLUP);             // ~0 µA while the button is open
  PCICR |= _BV(PCIE2); PCMSK2 |= _BV(PCINT18);

  DIDR0 = _BV(ADC0D) | _BV(ADC1D);            // no digital buffers on A0/A1
  TCCR1B = (TCCR1B & 0xF8) | 0x02;            // Timer1 /8 -> D9 PWM ≈ 1.96 kHz
  TIMSK0 &= ~_BV(TOIE0);                      // stop millis tick (keeps idle current low)
  power_twi_disable(); power_spi_disable(); power_timer2_disable();
#if DEBUG_SERIAL
  Serial.begin(9600);
  Serial.println(F("SolarLights Lite"));
#else
  power_usart0_disable();
#endif
  wdtSet(true);
}

void setLights(uint8_t pct, float vdd) {
  if (!pct) { digitalWrite(PIN_PWM, LOW); digitalWrite(PIN_STATUS, LOW); return; }
  float k = (vdd > LED_VF + 0.15) ? (COMP_REF_V - LED_VF) / (vdd - LED_VF) : 2.0;
  if (k < 0.6) k = 0.6;
  if (k > 2.0) k = 2.0;
  int cmp = pct * 2.55 * k;
  analogWrite(PIN_PWM, constrain(cmp, 1, 255));
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
  setLights(pct, vdd);
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
