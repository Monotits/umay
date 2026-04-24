# Why Your Voice Reveals More Than Your Words

We spend hours crafting text messages, rewriting emails, and editing social media posts. But the thing that reveals the most about our emotional state — our voice — goes almost completely unexamined. We built **Fenno** to change that. It's a **private voice mirror app for iOS** that analyzes how you sound, not what you say, using entirely on-device AI processing.

## The Gap Nobody Was Filling

Think about the tools you have for self-awareness. Mood journals track how you *think* you feel. Fitness trackers measure your body. Meditation apps guide your breathing. But nothing reflects back how you actually *sound* — the tension in your voice after a stressful meeting, the rising pace when you're anxious, the flat tone when you're emotionally checked out.

Research in **affective computing** and **paralinguistic analysis** has shown that vocal characteristics carry enormous emotional information. A 2019 study published in *Nature Human Behaviour* found that listeners can identify emotions from voice with higher accuracy than from facial expressions alone. Pitch contour, speaking rate, voice quality, and pause patterns all encode emotional states that we broadcast constantly but rarely notice in ourselves.

Voice analysis technology has existed in clinical and enterprise settings for years — call centers use it for sentiment detection, therapists use it in research settings, and security services use voiceprint matching. But these tools are expensive, cloud-dependent, and fundamentally designed for analyzing *other people's* voices. Nobody had built a simple, private, personal tool that lets you turn that lens on yourself.

That's what Fenno is: a **voice mirror**. Not a recorder, not a transcriber, not a coach telling you what to do. Just a mirror that shows you the version of yourself you hear least — the one everyone else hears.

## What Fenno Actually Measures

Fenno performs **real-time vocal analysis** across several dimensions, each chosen because research shows it correlates strongly with emotional and cognitive states:

**Tone and pitch analysis**: Fenno tracks your fundamental frequency (F0) and its variation over time. A monotone voice often signals fatigue or disengagement. High pitch variability can indicate excitement or anxiety. The app extracts pitch using **autocorrelation-based algorithms** running through Apple's **AVAudioEngine**, giving you a continuous readout of your tonal landscape without any perceptible latency.

**Speaking pace and rhythm**: Words per minute is the simplest metric, but Fenno goes deeper. It measures **inter-utterance pauses**, **speech-to-silence ratios**, and rhythmic consistency. Rushed speech with short pauses often maps to stress. Slow, deliberate speech with long pauses can indicate either deep thought or emotional heaviness. The patterns matter more than the raw number.

**Filler word detection**: "Um," "uh," "like," "you know," "basically," "actually" — Fenno identifies and counts these in real time. Filler words aren't inherently bad, but their frequency often increases under cognitive load or nervousness. Tracking them over time reveals patterns you'd never catch on your own. This feature alone has made Fenno popular with people preparing for presentations, job interviews, and podcasts.

**Emotional energy mapping**: Using a lightweight **Core ML classifier** trained on vocal affect datasets, Fenno maps your voice onto an energy-valence grid. High energy + positive valence = enthusiasm. Low energy + negative valence = exhaustion. This isn't about labeling your emotions — it's about showing you where your voice sits on the spectrum so you can notice shifts you might otherwise miss.

**Voice Pulse visualization**: All of these signals feed into Fenno's signature feature — a real-time visual "pulse" that represents your vocal state as a living, breathing waveform. It's designed to be glanceable. You don't need to read numbers or interpret charts. The pulse gives you an immediate, intuitive sense of your vocal energy.

## The Technical Architecture: Privacy as a Foundation

Every voice analysis app faces the same architectural decision: process in the cloud (easier, more powerful, less private) or process on-device (harder, constrained, but completely private). We chose on-device without hesitation, and then spent months making it work well within those constraints.

Fenno's **audio processing pipeline** is built entirely on Apple's native frameworks:

**AVAudioEngine** handles real-time audio capture and routing. We tap into the microphone input node and process audio buffers in 100ms windows — fast enough for real-time feedback, large enough for meaningful spectral analysis. The audio data never leaves this pipeline. It's processed, analyzed, and discarded within the same run loop.

**Accelerate framework** powers the DSP (digital signal processing) layer. Fast Fourier Transforms for spectral analysis, autocorrelation for pitch detection, and windowing functions for clean signal extraction all run through Apple's hardware-optimized vDSP library. This matters because voice analysis is computationally intensive, and running it on-device means we need every optimization available.

**Core ML** runs the emotional classification model. We trained a compact neural network (under 5MB) on labeled vocal affect datasets, then converted it to Core ML format for on-device inference. The model runs on the iPhone's **Neural Engine** when available, falling back to the GPU or CPU as needed. Inference time is under 15 milliseconds per window, which means zero perceptible delay in the voice pulse visualization.

**Speech framework** provides optional speech-to-text for filler word detection. This runs through Apple's on-device speech recognition (available since iOS 13), which processes audio locally without sending data to Apple's servers. We use it purely for identifying filler patterns — the actual words you say are not stored, logged, or displayed.

The result: **no recordings stored, no audio uploaded, no accounts required, no data leaving your iPhone**. Fenno is one of the few voice analysis tools where you can verify the privacy claim by simply turning on airplane mode. Everything still works.

## Who Uses a Voice Mirror?

When we first built Fenno, we assumed our primary users would be public speakers and communication coaches. We were only partially right. The actual user base turned out to be much more diverse:

**People processing emotions**: Therapists have told us their clients use Fenno between sessions as a check-in tool. "How do I actually sound right now?" is a surprisingly powerful question when you're working through anxiety, grief, or burnout. The voice doesn't lie the way journaling sometimes can — you can write "I feel fine" while your voice tells a completely different story.

**Remote workers and leaders**: When your communication is primarily through video calls, your voice becomes your primary expressive tool. Several users have told us they check Fenno before important calls to calibrate their energy. One engineering manager described it as "a vocal warm-up mirror — I can see if I sound tired before my team does."

**Language learners**: Non-native speakers use Fenno to track their intonation patterns, speaking pace, and filler word usage in their target language. The real-time feedback helps them notice habits that are invisible in written practice.

**Content creators and podcasters**: Vocal consistency matters when you're recording content. Fenno helps creators identify when their energy drops, when they're using too many fillers, or when their pace drifts. It's become a pre-recording ritual for several podcast hosts.

**Anyone curious about self-awareness**: A surprising number of users simply find it fascinating to see their voice reflected back as data. There's something compelling about watching your emotional energy shift in real time as you talk through your day.

## Why "Mirror" and Not "Coach"

We deliberately chose the word **mirror** instead of coach, trainer, or analyzer. This distinction matters deeply to the product philosophy.

A coach tells you what to do. A mirror shows you what is. Fenno doesn't say "speak slower" or "use fewer filler words" or "sound more confident." It shows you your vocal patterns and lets you decide what, if anything, to change. This is the same philosophy behind **ShadowART**, our Jungian shadow work journal — reflection over prescription, awareness over instruction.

We've found that people change more effectively when they see their own patterns clearly than when they're told what to fix. A person who notices they use "um" 40 times in a 5-minute conversation will naturally start reducing it — no coaching required. Someone who sees their energy flatline every afternoon might adjust their schedule, or at least understand why their evening calls feel harder.

The mirror metaphor also drives our design decisions. The interface is minimal. The data is presented visually, not numerically. The voice pulse is designed to feel like looking at yourself, not reading a medical chart.

## The Science of Vocal Self-Perception

There's a well-documented phenomenon in psychology called **vocal self-confrontation** — the discomfort people feel when hearing their own recorded voice. Research by Holzman and Rousey (1966) and later studies have shown that this discomfort comes from the gap between how we think we sound (through bone conduction) and how we actually sound (through air conduction).

Fenno sidesteps this discomfort entirely. Because it doesn't play back your voice, you never experience that jarring moment of hearing a recording. Instead, you see abstract representations of your vocal qualities — energy levels, pace patterns, tonal contours. It's the information without the cringe factor.

This turns out to be a much more effective path to vocal self-awareness. Users engage with the data more consistently because they're not fighting the instinct to stop listening to themselves. They build a relationship with their voice as a set of patterns, not as a sound they may or may not like.

Recent research in **interoception** — the ability to sense your body's internal states — suggests that better awareness of physiological signals leads to better emotional regulation. Your voice is one of the most accessible physiological signals you produce. Fenno turns it into something you can actually observe and learn from.

## Pricing and Availability

**Fenno** is available on the [App Store for iPhone](https://apps.apple.com/us/app/fenno-private-voice-mirror/id6761913486). The free tier includes core voice analysis features. For users who want detailed pattern tracking, emotional lenses, and historical comparisons, Fenno offers monthly ($4.99/month), yearly ($29.99/year), and lifetime ($79.99) plans. Every plan includes a free trial so you can experience the full mirror before committing.

## What We Learned Building Fenno

Building a real-time voice analysis app taught us several things that will influence everything we build next:

**On-device AI is ready**. Two years ago, running a neural network for vocal affect classification on an iPhone would have been painfully slow. Today, with the Neural Engine and Core ML optimizations, it's imperceptible. The gap between cloud AI and on-device AI is closing fast, and for privacy-sensitive applications, on-device is already good enough.

**Privacy isn't a feature — it's an architecture**. You can't bolt privacy onto a cloud-based system. With Fenno, privacy is the foundation. There's no server to breach, no database to leak, no API to intercept. This is the same principle we applied to **Pulse Guard** and **ShadowART**, and it continues to define how we build at umay.dev.

**The best self-awareness tools are mirrors, not judges**. People don't want another app telling them they're doing something wrong. They want to see themselves clearly and make their own decisions. This insight shaped Fenno's entire UX and it's now a core design principle across our studio.

Your voice carries more truth than your carefully chosen words. Fenno just makes it visible. We're building this at [umay.dev](https://umay.dev), and we think the future of personal AI is private, on-device, and designed to reflect — not to judge.
