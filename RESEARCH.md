# The Story Behind CompanionHK (港伴AI)

## A City That Never Sleeps, But Quietly Suffers

Hong Kong glows. From Victoria Peak, the skyline is a wall of light — 7.5 million people stacked into 1,114 km² of concrete, glass, and ambition. It is one of the most connected, most productive, most densely populated cities on earth. Yet behind the neon, millions face a quieter reality: pervasive loneliness, relentless pressure, and a mental health system that cannot keep up. CompanionHK was built because this city deserves a companion that is always there, always safe, and always speaks its language.

---

## The Problem: Hong Kong by the Numbers

### Loneliness Epidemic (孤獨危機)

Hong Kong is experiencing a loneliness crisis that cuts across generations.

Among the elderly, the proportion experiencing moderate or severe loneliness has nearly **doubled** — from 35.3% in 2018 to **68.3% in 2024** [1]. Over half (53%) of residents aged 65 and above experienced social isolation in 2023–24, up from 41.2% just six years earlier [2]. The emigration wave has deepened this wound: 63% of elderly with emigrant children are at "high risk" of social isolation, with 46% now living alone [3]. Nearly half (49.6%) of these parents show signs of depression [3].

But loneliness is not only an elderly problem. Young adults — unmarried, overworked, confined to tiny flats — are increasingly isolated too. Among men aged 25–39 who died by suicide in 2024, 72.7% had never been married, compared to 44% in the general population [4].

### Mental Health Crisis (精神健康危機)

Hong Kong's suicide rate reached **14.1 per 100,000** in 2024, up from 13.5 the year before. The age-standardized rate of 10.6 **exceeds the global average** of 8.9 reported by the WHO [5]. The sharpest rise is among young men aged 25–39, whose rate climbed from 10.0 in 2021 to 14.4 in 2024 [4]. Financial stress, unemployment, and social isolation are the primary drivers.

And for those who struggle, help is hard to find. Hong Kong has roughly **460 psychiatrists for 7.5 million people** — a ratio of 1:761, far below WHO recommendations [6]. Public psychiatric waiting times stretch up to **99 weeks** in some districts [7]. Less than 30% of people with mental health conditions ever seek support [7].

### Student Pressure (學業壓力)

For Hong Kong's young people, academic pressure is the defining stressor.

**40% of HKDSE students** show symptoms of depression or anxiety [8]. Among secondary students broadly, 42.6% report stress levels of 7–10 on a ten-point scale, and academic issues have been the **top source of concern for five consecutive years** [9]. The HKFYG's wellness platform handled 25,842 emotion-related cases in 2024–25, up sharply from 18,920 the year before [9].

Perhaps the most alarming statistic: **59.6% of students rarely or never sought help**, and 65.4% had never reached out to any individual or organisation [9]. The support exists — but the bridge to reach it does not.

### Work-Life Imbalance (工作壓力)

Hong Kong has the **world's longest working week**. Employees average over 50 hours per week — roughly 2,600 hours per year, about 1,000 more than workers in Paris [10]. A union survey found that over 50% log more than 45 hours weekly, with 7.3% exceeding 70 hours [11]. Nearly 70% are expected to respond to work messages outside office hours [11].

The toll: **87% of employees suffer from work stress** [12]. Hong Kong ranks just 46th globally for work-life balance [13]. Workers get only 17.2 days of paid leave per year, below the 23-day global average [10].

### Housing and Living Conditions (住屋困境)

Over **200,000 people** live in subdivided flats (劏房) averaging just 65 square feet — roughly half a parking space [14]. Hong Kong has been ranked the world's most unaffordable city for 14 consecutive years [14]. Research shows that spaces smaller than 13 m² are associated with increased anxiety and depression, and residents experience family conflicts, physical strain, and housework burnout in addition to mental distress [15].

---

## Why an AI Companion?

The numbers paint a clear picture: demand for emotional support in Hong Kong vastly outstrips supply. Traditional pathways are blocked by structural barriers:

- **Stigma**: Mental health stigma remains high. Many prefer anonymous, low-barrier channels over face-to-face professional encounters [16].
- **Professional shortage**: With a 1:761 psychiatrist ratio and wait times approaching two years, accessible alternatives are not a luxury — they are a necessity [6][7].
- **Youth reluctance**: When 59.6% of students never seek help, the threshold must be lowered radically. An always-available, non-judgmental AI meets users where they already are — on their phones, in their language [9].
- **Research support**: A systematic review of chatbot-delivered mental health interventions found **significant reductions in psychological distress** among young people [17]. A pilot RCT in Hong Kong compared an AI chatbot with a nurse hotline for reducing anxiety and depression, with promising feasibility results [18].
- **Intergenerational potential**: Research shows that internet-mediated support can moderate the relationship between intergenerational distance and loneliness among older adults [19].

CompanionHK does not replace therapists. It fills the gap between suffering in silence and finding professional help — a warm, safe, culturally fluent first point of contact.

---

## Our Answer: CompanionHK (港伴AI)

CompanionHK is a multi-role AI companion designed specifically for Hong Kong. It offers three distinct role spaces, each mapped to a core problem:

### Companion (情感夥伴) — Addressing Loneliness and Emotional Distress

An always-available empathetic presence that uses the **REFLECT → VALIDATE → EXPLORE → SUPPORT** framework. It detects emotional states — loneliness, anxiety, anger, grief, joy — and responds with culturally appropriate warmth. It speaks natural Cantonese (口語), not formal written Chinese (書面語), because comfort requires familiarity. When crisis signals are detected, a two-tier safety system immediately surfaces verified Hong Kong hotlines.

### Local Guide (本地嚮導) — Combating Isolation Through Reconnection

Loneliness often lives in inertia — staying in the 劏房, not knowing where to go, not having the energy to decide. The Local Guide generates mood-aware, weather-aware place recommendations scored by relevance, distance, weather fit, and personal preferences. Powered by Google Maps with real routing and travel time, it suggests social-friendly spots: 茶餐廳 for communal dining, 街市 for neighbourhood life, 行山 trails for fresh air. It turns "I don't know what to do" into "here's somewhere nearby that fits how you feel right now."

### Study Guide (學習助手) — Easing Academic Pressure

Built with awareness of Hong Kong's DSE system — grading scales, exam calendars, past paper formats — the Study Guide breaks overwhelming workloads into manageable goals. It supports bilingual EMI/CMI contexts, uses Hong Kong-specific examples (MTR distances for physics problems, Hang Seng Index for statistics), and celebrates small wins. It reminds students that one bad result does not define them, and gently encourages breaks, sleep, and balance.

---

## Safety as a Product Requirement

Safety is not a stretch goal in CompanionHK — it is a foundational design constraint.

- **Two-tier crisis detection**: An ML-based safety model (MiniMax) evaluates every message for risk level, emotion, and required policy action. A rule-based fallback catches high-risk keywords in English and Chinese if the model is unavailable.
- **Crisis resource banner**: When escalation is triggered, the app immediately displays verified Hong Kong hotlines — The Samaritans (2896 0000), Suicide Prevention Services (2382 0000), The Samaritan Befrienders (2389 2222), and Emergency Services (999).
- **Hard safety boundary**: The AI never provides procedural harm guidance, even when asked indirectly. It responds with calm, compassionate refusal and encourages professional contact.
- **Continuous monitoring**: Emotion and safety-risk scoring runs on every turn, adapting the UI tone, theme, and prompt context in real time.
- **Audit trail**: All safety events are persisted for accountability and review.

---

## Designed for Hong Kong (為香港而設)

Every design decision reflects the city CompanionHK serves:

- **Weather-adaptive UI**: The interface shifts with Hong Kong's weather — typhoon warnings, summer heat, rainy days — through 10+ CSS theme states driven by real-time Open-Meteo data.
- **Cantonese voice**: A voice pipeline with Cantonese.ai for native Cantonese ASR/TTS alongside ElevenLabs for English, with adapter-based fallback.
- **Local vocabulary**: The AI naturally uses terms like 茶餐廳, 大排檔, 叮叮, 小巴, 街市, 糖水, 離島 — because sounding local *is* feeling local.
- **Neighbourhood awareness**: Recommendations reference specific areas — 深水埗 for street food, 中環 for fine dining, 西環 for hidden gems — with MTR stations and bus routes included.
- **Cultural sensitivity**: Emotional support respects Hong Kong norms — it does not push Western therapy framing but meets users in their own cultural context.

---

## Technology in Service of Empathy

The tech stack exists to make support feel natural, not robotic (see [ARCHITECTURE.md](ARCHITECTURE.md) for details):

- **Hybrid memory**: Redis for short-term conversational context, PostgreSQL for durable user preferences, pgvector for semantic recall — so the AI remembers what matters to each user and grows with them over time.
- **Provider resilience**: Every external service sits behind an adapter with graceful degradation. If a provider goes down, the companion stays up. The AI is always available.
- **Contextual awareness**: Weather data, emotion signals, and user preferences feed into every interaction. Recommendations are not generic — they are shaped by how the user feels, what the sky looks like, and what they have enjoyed before.

---

## Future Vision: Family Mode (家庭模式)

Research consistently shows that **family communication is the strongest protective factor** against loneliness in Hong Kong's elderly [19][20]. CompanionHK's planned Family Mode will create an intergenerational bridge:

- Generate short, respectful summary cards that users can share with family members — turning "I don't know how to explain how I feel" into a gentle, structured message.
- Bridge the physical distance between emigrant children and elderly parents left behind.
- Maintain strict privacy controls: nothing is shared without explicit user consent.

Because sometimes the hardest conversation is the most important one, and a little help starting it can change everything.

---

## References

1. Chinese University of Hong Kong & The Salvation Army. (2024). Study on elderly loneliness in Hong Kong. Reported in *South China Morning Post*, "Proportion of elderly Hongkongers struggling with moderate or severe loneliness almost doubles since 2018."
2. SCMP. (2024). "Experts sound alarm as growing number of Hong Kong elderly become socially isolated."
3. Hong Kong Christian Service. (2024). "Survey on Service Needs of Elders with Emigrant Children in Hong Kong."
4. HKU Centre for Suicide Research and Prevention. (2025). "2024 Suicide Rates in Hong Kong" — press release and World Suicide Prevention Day slides.
5. World Health Organization. (2021). Global age-standardized suicide rate data. Cited in HKU CSRP 2024 report.
6. The Standard. (2024). "Hopes gone and faith lost with psychiatrist to patient ratio at 1:761, say two top docs."
7. Mind HK. (2024). "2024 Policy Recommendations for Hong Kong." Also: HKSAR Government LCQ response on psychiatric consultation and treatment (July 2023).
8. Hong Kong Council of Social Service. (2024). "40% of Surveyed HKDSE Students Show Symptoms of Depression or Anxiety."
9. Hong Kong Federation of Youth Groups. (2025). "Back-to-school survey reveals rising anxiety and steady stress levels among secondary students." Also: HKFYG. (2024). "Youth Mental Health Conditions survey."
10. UBS. (2018). "Prices and Earnings" global city comparison. Also: China Daily, "HK has world's longest working week."
11. SCMP. (2023). "How overworked are Hongkongers? More than half of employees log over 45 hours a week, some longer than 70 hours: union survey."
12. Mental Health Association of Hong Kong. Work stress survey data. Cited in APRIL International health guide.
13. Hong Kong Business. (2024). "Hong Kong ranks 46th globally for work-life balance."
14. Reuters. (2024). "Hong Kong struggles to improve conditions in tiny, crowded homes."
15. Springer Nature / BMC Public Health. (2024). "The effect of dwelling size on the mental health and quality of life of female caregivers living in informal tiny homes in Hong Kong."
16. Cambridge University Press / BJPsych Open. (2025). "Changes in mental health stigma and well-being: knowledge, attitudes and behavioural intentions among Hong Kong residents between 2021 and 2023."
17. Hong Kong Polytechnic University. (2024). "Chatbot-Delivered Interventions for Improving Mental Health Among Young People: A Systematic Review and Meta-Analysis." Published via PolyU Institutional Research Archive.
18. PMC / JMIR. (2025). "Comparison of an AI Chatbot With a Nurse Hotline in Reducing Anxiety and Depression Levels in the General Population: Pilot Randomized Controlled Trial."
19. Frontiers in Public Health. (2024). "The effect of intergenerational support from children on loneliness among older adults — the moderating effect of internet usage and intergenerational distance."
20. Frontiers in Psychology. (2022). "Intergenerational relationship quality, sense of loneliness, and attitude toward later life among aging Chinese adults in Hong Kong."
