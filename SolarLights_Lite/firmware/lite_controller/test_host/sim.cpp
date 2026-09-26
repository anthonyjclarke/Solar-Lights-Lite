// Host test: c++ -std=c++17 -I../include sim.cpp -o sim && ./sim
#include <cstdio>
#include <cmath>
#include "schedule.h"
using namespace lite;
static const char* NM[] = {"DAY","EVENING","OVERNIGHT","PREDAWN","LVC"};

double panelAt(double h) { double t = fmod(h, 24); return (t >= 6.75 && t < 17.25) ? 6.0 : 0.2; } // Sydney June

void run(const char* title, float (*vddAt)(double), bool allNight, int days, bool stage1 = false) {
  printf("\n== %s ==\n", title);
  Scheduler s;
  if (stage1) { s.cfg.capPct = 20; s.cfg.predawn = false; }
  s.begin(allNight, stage1);
  int lastState = -1, lastPct = -1;
  double wh = 0;      // lit %·h
  long t = 0, fastSecs = 0;
  while (t < days * 86400L) {
    double h = 12 + t / 3600.0;
    float v = vddAt(h);
    double p = panelAt(h);
    bool fast = s.needFastTick();
    uint32_t dt = fast ? 1 : 8;
    t += dt; if (fast) fastSecs += dt;
    uint8_t pct = s.step(dt, v, p < 1.5, p > 3.0);
    wh += pct * dt / 3600.0;
    bool steady = (pct == 0 || pct == s.eveningPct || pct == 20 || pct == s.cfg.allNightPct);
    if (s.state != lastState || (pct != lastPct && steady)) {
      double tt = fmod(h, 24);
      printf("day%d %02d:%02d  %-9s %3u%%  learned=%d night=%lumin\n", (int)(h / 24), (int)tt,
             (int)((tt - (int)tt) * 60), NM[s.state], pct, s.learned, (unsigned long)(s.nightLen / 60));
      lastState = s.state; lastPct = pct;
    }
  }
  printf("avg lit load: %.0f mAh/day at 200 mA full · 1 s wakes %.1f h/day\n", wh / 100.0 * 200 / days, fastSecs / 3600.0 / days);
}
float vGood(double) { return 3.90f; }
float vSag(double h) { return (h > 20 && h < 30) ? 3.25f : 3.70f; }
int main() {
  run("3 winter days, battery 3.90 V", vGood, false, 3);
  run("LVC at 20:00 then recovery", vSag, false, 2);
  run("All-night jumper", vGood, true, 2);
  run("Stage 1: existing 1.2 W panel profile", vGood, false, 3, true);
}
