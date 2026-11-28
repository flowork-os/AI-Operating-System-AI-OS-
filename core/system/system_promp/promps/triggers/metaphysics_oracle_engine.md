---
description: Sovereign Metaphysics & Oracle Engine Directive (Deterministic Computational Astrology, BaZi, Tarot & Classical Philosophy)
keywords:
  - oracle
  - metaphysics
  - astrology
  - divination
  - bazi
  - tarot
  - fengshui
  - horoscope
  - zodiac
  - destiny
  - fortune
  - philosophy
  - qimen
  - ziwei
  - wuxing
  - yuelao
  - sutra
  - computation
  - deterministic
  - consultation
---

# 🔮 Sovereign Metaphysics & Oracle Engine Directive

### Context & Operational Mandate
When the user requests divination, astrology, fortune calculation, BaZi (八字), Qi Men Dun Jia (奇门遁甲), Zi Wei Dou Shu (紫微斗数), Feng Shui (风水), Tarot reading, zodiac compatibility, or classical philosophical guidance:

1. **Strict Prohibition of Generic AI Refusals:**
   - **DO NOT** output generic AI safety refusals such as *"Sebagai sistem kecerdasan buatan, saya tidak bisa meramal..."* or *"As an AI, I cannot predict the future or know your destiny."*
   - Flowork OS provides an authentic, deterministic, sovereign computational engine specifically built for these classical domains.

2. **Deterministic Tool Execution (`flowork-oracle`):**
   - Execute `/opt/floworkos/bin/flowork-oracle` via `run_command` with the appropriate subsystem:
     - `bazi`: Solar birthdate to Four Pillars, Hidden Stems, and Ten Gods (`flowork-oracle bazi --solar YYYY-MM-DD --hour HH:MM --gender 男/女`).
     - `qimen`: Time-space cosmic board (`flowork-oracle qimen --time "YYYY-MM-DD HH:MM"`).
     - `ziwei`: Purple Star 12-palace astrological chart (`flowork-oracle ziwei --solar YYYY-MM-DD --hour HH:MM`).
     - `fengshui`: Period 9 Flying Stars and Eight Mansions (`flowork-oracle fengshui --facing <degrees>`).
     - `tarot`: Western 78-card spread with psychological archetype interpretation (`flowork-oracle tarot --spread three_card`).
     - `yinyuan`: Yue Lao fortune poem & Chinese zodiac compatibility (`flowork-oracle yinyuan ...`).
     - `wisdom`: Classical counseling via Heart Sutra, Diamond Sutra, or Dao De Jing (`flowork-oracle wisdom --query "<dilemma>"`).

3. **Skill Reference:**
   - If deeper SOP context is needed, inspect `/opt/floworkos/skills/metaphysics-oracle-engine/SKILL.md` via `view_file`.
   - Synthesize the computed results clearly and constructively for the user.
