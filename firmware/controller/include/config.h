/*
 * Solar Lights Lite – controller settings
 * ---------------------------------------
 * Every user-tuneable value lives here. The file is hardware-independent, so
 * it is shared by the firmware and by the host regression tests in test_host/.
 */
#pragma once
#include <stdint.h>

// Printed as fw= in every telemetry line and shown in Home Assistant.
constexpr char FW_VERSION[] = "0.6.0";

// ------------------------------------------------------------ pins
constexpr uint8_t PIN_LED_PWM = 9;  // D9 / OC1A -> R3 47 ohm -> low-power LED string +
constexpr uint8_t PIN_LDR_PWR = 7;  // D7 powers the LDR divider only while sampling
constexpr uint8_t ADC_LDR     = 1;  // A1: LDR / R4 midpoint (ADC channel number)
constexpr uint8_t PIN_BUTTON  = 2;  // D2: test button to GND, internal pull-up
constexpr uint8_t PIN_TX      = 1;  // D1/TX: telemetry to the D1 Mini through Q2

// ------------------------------------------------------------ lighting
// Dusk-to-dawn PWM duty. R3 and the pin set the LED current; duty only sets
// brightness. Lower it to trade brightness for run time.
constexpr uint8_t  NIGHT_DUTY_PCT   = 100;
constexpr uint8_t  STARTUP_TEST_PCT = 60;   // brief flash after reset; capped at night duty
constexpr uint16_t STARTUP_TEST_S   = 10;
constexpr uint8_t  BUTTON_TEST_PCT  = 100;  // D2 press; capped at night duty
constexpr uint16_t BUTTON_TEST_S    = 60;
constexpr uint8_t  FADE_STEP_PCT    = 2;    // % per second at dusk and dawn

// ------------------------------------------------------------ light sensor
// A1 as a fraction of VCC with R4 = 47k. Dark below ~0.30 means the LDR is
// above ~110k; light above ~0.60 means it is below ~31k. The gap between the
// two thresholds prevents flicker. Calibrate in the final mounting position.
constexpr float    LDR_DARK_RATIO       = 0.30f;
constexpr float    LDR_LIGHT_RATIO      = 0.60f;
constexpr uint16_t TRANSITION_CONFIRM_S = 300;  // dark or light must persist this long

// ------------------------------------------------------------ battery protection
constexpr float    LOW_BATT_V   = 3.45f;  // below: night duty is halved
constexpr float    LVC_OFF_V    = 3.30f;  // below for LVC_HOLD_S: lights off (low-voltage cut-off)
constexpr uint16_t LVC_HOLD_S   = 30;
constexpr float    LVC_RESUME_V = 3.60f;  // cut-off clears above this, in confirmed daylight

// ------------------------------------------------------------ calibration
// Internal bandgap used to measure VCC. Calibrate once against a meter:
// BANDGAP_V = 1.10 * Vmeter / Vreported.
constexpr float BANDGAP_V = 1.10f;

// ------------------------------------------------------------ timing
// The watchdog oscillator is uncalibrated and varies by chip: a scheduler
// "second" is typically 10-20% longer than a real one (12% and 16% measured).
// Dusk-to-dawn operation does not depend on wall-clock time.
constexpr uint16_t TIME_SCALE = 1;  // bench only: 60 makes each real second count as a minute

// Telemetry cadence, in scheduler seconds.
constexpr uint16_t STATUS_INTERVAL_S        = 8;   // production: one compact line
constexpr uint16_t ADVANCED_ACTIVE_REPORT_S = 10;  // advanced: while confirming, testing or in cut-off timing
constexpr uint16_t ADVANCED_IDLE_REPORT_S   = 60;  // advanced: stable-state heartbeat
