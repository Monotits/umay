# Why We Built Pulse Guard

Traditional home security has always felt broken to us. You install cameras everywhere, pay monthly subscriptions to cloud providers, worry about privacy while watching your own home, and still need to buy dedicated hardware. The whole setup screams 90s security theater. We knew there had to be a better way.

## The Problem We Couldn't Ignore

The home security market feels stuck in time. Here's what frustrated us:

**Privacy paradox**: To protect your privacy, you install cameras that destroy it. You're collecting footage of yourself, your family, your guests. Then it goes to some company's servers, getting processed by AI models you don't control, stored indefinitely, and vulnerable to breaches.

**Hardware bloat**: A security system meant for detecting presence requires purchasing separate motion sensors, WiFi hubs, cloud subscriptions, and cameras. Your desk becomes a graveyard of blinking boxes. For something as simple as "is someone home?", this feels wasteful.

**Cost creep**: Between the hardware, the monthly fees, and the increasingly aggressive upselling of "smart" features, the total cost of ownership is brutal. Most people just give up and leave things unsecured.

**Unreliability**: Motion sensors miss people moving slowly. Cameras fail in poor lighting. Cloud connections drop. You end up not trusting the system enough to actually rely on it.

We started asking: what if you could detect human presence without any of this baggage?

## The Insight That Changed Everything

The breakthrough came when we stumbled onto research in WiFi sensing. For years, security researchers and academics have known something fascinating: **WiFi signals are incredibly sensitive to human movement**. Every time a person walks, breathes, or even shifts their weight, they distort the electromagnetic waves bouncing through a room.

This isn't theoretical—it's physics. WiFi operates on the 2.4 GHz and 5 GHz bands. These frequencies interact with the human body in predictable ways. When you move through a WiFi signal's path, you create minute disturbances. Those disturbances are measurable. They're quantifiable. They're usable.

More importantly: **this data never leaves your device**. There's no image, no face, no identifying information. Just signal patterns. It's the most privacy-respecting way to detect presence possible.

## How Pulse Guard Actually Works

Here's the technical magic that makes this work:

Your MacBook's WiFi chip continuously measures something called **Channel State Information (CSI)**. This is the detailed state of the wireless channel—essentially a fingerprint of how the signal is being affected by everything in the room. WiFi drivers collect this data constantly; it's just usually discarded.

Pulse Guard intercepts that CSI data and applies signal processing algorithms to extract movement patterns. When someone is present and moving, the CSI fluctuates in specific ways. Our algorithms learned to recognize these patterns during development. Static objects, dead air, network noise—all have signatures we can distinguish from actual human movement.

The processing pipeline looks like this:

1. **CSI collection**: Raw channel state data from your WiFi card, updated hundreds of times per second
2. **Signal preprocessing**: Filtering out noise and stabilizing the baseline measurement
3. **Feature extraction**: Converting raw CSI into meaningful movement indicators
4. **Classification**: Machine learning models determine if the patterns match human presence
5. **Temporal filtering**: Smoothing out false positives using time-series analysis

All of this happens locally, on your machine. No data leaves. No cloud calls. No third parties involved.

## Why macOS Was the Right Choice

Building this required deep access to WiFi hardware and system frameworks. We considered Windows, Linux, even building our own hardware.

macOS won because of **CoreWLAN**—Apple's native WiFi API. Unlike Windows (where WiFi access is intentionally restricted for security), or Linux (where driver compatibility is a nightmare), macOS lets us interact with the WiFi stack in a controlled, stable way. We get the CSI data we need without jailbreaking or exploiting system vulnerabilities.

Beyond that, the macOS ecosystem just feels right for this kind of system software. The kernel is stable. The frameworks are well-designed. We could build something that integrates cleanly into the system without requiring users to disable security features.

Plus, Mac users tend to care about privacy. They're our audience.

## The Privacy-First Architecture

This is where we genuinely differ from everything else on the market:

**No cameras**: Zero visual data collection. Ever.

**No cloud**: There is no cloud component. Your data doesn't sync anywhere. Your presence patterns stay on your device.

**No training**: We don't need to train models on your specific home. The detection models are universal—they work in any environment because they're looking for the fundamental physics of human movement, not environmental specifics.

**No server backend**: There's nothing running on a server about you. No account, no login, no personal data stored anywhere except your Mac's local storage.

**Open processing**: You can inspect exactly what's happening. The algorithms aren't a black box. The architecture is transparent.

This is genuinely different. Most "privacy-focused" products are just marketing fluff. We built something where privacy is architectural, not aspirational.

## What Pulse Guard Enables

Right now, Pulse Guard detects presence in a room. That's it. But that simple capability opens surprising possibilities:

- **Smarter home automation**: Lights turn on only when the room is actually occupied, not just when motion is detected
- **Energy savings**: HVAC systems know which rooms are in use
- **Security basics**: When you leave, you know nobody unexpected is inside
- **Better notifications**: Smart home events that actually understand context

We're already seeing users build interesting workflows around this.

## What's Next

We have plans for Pulse Guard that go beyond basic presence detection:

**Zone-based detection**: Instead of "is anyone home?", detect which specific rooms are occupied. This requires mapping CSI responses to spatial location, a harder problem but fundamentally solvable.

**Multi-room support**: Coordinate detection across multiple Macs to get a whole-home picture of presence patterns.

**Occupancy patterns**: Learn when you're typically home, create intelligent automations based on your actual schedule.

**Integration ecosystem**: APIs for developers to build on top of local presence data.

All of this stays local. All of it respects privacy. None of it requires new hardware.

## Why This Matters

Building Pulse Guard forced us to confront a question: **what does security mean when it destroys the very privacy it's supposed to protect?**

Traditional approaches answer this with cameras and cloud. We answered it differently. We asked what technology could actually work without requiring you to sacrifice privacy for safety. It turned out the answer was right there in the WiFi signals we all ignore.

There's something deeply satisfying about this. A WiFi router that came with your Mac, doing something useful it was never designed to do. No new hardware. No subscriptions. No compromise.

That's what Pulse Guard is. Not a camera system. Not a motion sensor array. Just your Mac getting a little smarter about what's happening in its space, while respecting the fact that this space is *yours*.

We think the future of home security looks like this: less intrusive, more intelligent, genuinely private. We're building it at umay.dev.
