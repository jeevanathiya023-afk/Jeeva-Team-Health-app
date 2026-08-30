# SeniorEase — Design Principles for Elderly Users (60+)

This document details the ergonomic, psychological, and visual design rationale behind every decision made in **SeniorEase**.

---

## 1. Ergonomic & Visual Accessibility

### A. Scalable Typography (85% to 140%)
- **Why**: Age-related macular degeneration, presbyopia, and cataracts cause significant loss in fine visual acuity.
- **Implementation**: The base font size is set to `18px` by default and dynamically scales up to `calc(18px * 1.4) = 25.2px` with proportional heading scaling up to `61.6px`.
- **Font Choices**: Modern geometric sans-serif (`Outfit`) with wide open apertures, clear distinction between `1`, `l`, and `I`, and `Mukta Malar` for ultra-legible Tamil rendering.

### B. High Contrast Mode (WCAG AAA)
- **Why**: Contrast sensitivity drops sharply after age 60, making pastel colors or gray-on-white text unreadable.
- **Implementation**: High Contrast mode applies pure black backgrounds (`#000000`) with high-luminance yellow text and borders (`#FFE600`), achieving a contrast ratio exceeding **18:1** (far above WCAG AAA requirement of 7:1).
- **Eye-Care Sepia Mode**: Reduces blue light strain for seniors sensitive to bright backlights during evening use.

### C. Touch Target Sizing (Minimum 58px)
- **Why**: Reduced fine-motor control, hand tremors, and arthritis make small touch targets frustrating and error-prone.
- **Implementation**: All buttons, cards, and input fields adhere to a minimum touch target height of `58px` to `84px`, with generous spacing (`12px` to `24px` margins) to prevent accidental neighboring clicks.

---

## 2. Information Architecture & Navigation

### A. Flat, Single-Level Hierarchy
- **Why**: Deeply nested dropdown menus, hamburger menus, and multi-tiered breadcrumbs create cognitive disorientation for elderly users who struggle with spatial memory in software.
- **Implementation**: Every feature is accessible in exactly **1 click** from the Home screen. Every subpage displays an unambiguous "⬅️ Back to Home" button.

### B. The 4 Spatial Orientation Questions
Every screen in SeniorEase explicitly answers:
1. **Where am I?** — Visible breadcrumb badge with icon.
2. **What can I do here?** — Plain language subtitle and large action cards.
3. **How do I go back?** — Prominent left-aligned Back button.
4. **What happens when I click this button?** — Verb-first labels (e.g., *"Open Doctors & Hospitals"*, *"Mark as Taken"*, *"Test Sound Chime"*).

---

## 3. Plain Language vs. Technical Jargon

Elderly users should never feel intimidated or blamed by the software.

| Technical Jargon (Forbidden) | SeniorEase Human Language |
|---|---|
| *Authentication / Credentials* | **Sign in / Your Information** |
| *Configure settings* | **Change settings** |
| *Geolocation coordinates* | **Your current location** |
| *Invalid input / Validation error* | **Please check the information entered** |
| *Session expired* | **You have been signed out safely** |
| *Dismiss modal* | **Close / Done** |
| *Execute query* | **Search / Find** |

---

## 4. Audio Feedback & Gentle Sounds

- **No Jarring Buzzers**: Harsh beep sounds can trigger anxiety. SeniorEase uses the Web Audio API to generate soft dual-tone sine and triangle harmonic chimes (`C5 -> E5 -> G5`).
- **Immediate Confirmation**: Actions like marking a pill as taken or booking a doctor trigger instant audio feedback and celebratory toasts (*"🎉 Great job! Telmisartan marked as taken."*).

---

## 5. Emergency Safety & Mistake Tolerance

- **Accidental Click Protection**: Seniors often accidentally tap large buttons. The Emergency SOS feature includes a **5-second countdown with visual and audio cues**, accompanied by a large **"❌ Cancel Alert (Mistake)"** button.
- **Reversibility**: Medicines marked as taken can be easily undone with a single tap on *"Undo Taken"*.
