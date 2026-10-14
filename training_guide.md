# Workshop: "Reading School Climate & Attendance Data"

A 30-minute session for non-technical staff (teachers, principals, program managers).
Goal: help people interpret school data correctly and use it in planning, without needing to code.

Examples below come from the analysis in this repo (648 Chicago Public Schools).

## Learning goals
By the end, participants can:
1. Say what chronic truancy, attendance, and the 5Essentials climate ratings measure. (Check the current CPS definition of chronic truancy and read it out; this repo doesn't define it.)
2. Read a scatter plot and a box plot.
3. Explain why "related to" does not mean "causes."
4. Name two questions they would ask before acting on a number.

## Agenda
| Time | Activity |
|---|---|
| 0-5 min | Why this matters: "Do schools where students report feeling safer have less truancy?" |
| 5-12 min | Walk through the charts: truancy by school type, safety vs truancy, on-track vs graduation. For each, ask the room what they notice before you explain. |
| 12-20 min | Pitfalls (below), using examples from the charts |
| 20-27 min | Small-group discussion: "Pick one school type. What would you want to know next before changing anything?" |
| 27-30 min | Wrap-up and the 3-question feedback survey |

## Key messages (with real numbers from this analysis)
- **Correlation is not causation.** Student-reported safety and chronic truancy have a correlation of -0.54: schools with higher safety ratings tend to have lower truancy. That doesn't tell us which causes which, or whether something else drives both.
- **School averages are not students.** A school-level number can't tell you what any one student experiences.
- **Missing data is information.** 493 of 648 schools report an SAT average of 0, which means "no score," not a score of zero. The regression had to drop about 16% of schools (103 of 648) because of missing survey ratings.
- **Small groups are noisy.** Classical schools (n=6) have a median truancy of 11.2%, but with so few schools that number can swing easily.
- **Ask what "good" is compared to.** High schools have a median chronic truancy of 66.5% vs 40.1% for elementary schools, so comparing a high school to the overall average would be misleading.
- **Two measures can be the same thing.** Chronic truancy and student attendance correlate at -0.98. Showing both as separate evidence would double count.

## Facilitator notes
- Use plain words: "share of students who are chronically truant," not "regression coefficient."
- Pause after each chart and ask "What do you notice?" first.
- Bring one printed handout (below) per person.

## One-page handout (give this to participants)

**What the data does tell us**
- How schools compare on attendance, climate surveys, and outcomes.
- Where patterns are strong enough to be worth a closer look.

**What it doesn't tell us**
- Why a pattern exists.
- What any individual student or classroom is experiencing.

**Before acting on a number, ask:**
1. How many schools or students is this based on?
2. How much data is missing?
3. What else could explain this?
4. Compared to what?

## Feedback survey (collect with a free Google Form)
1. How confident are you in reading a chart like these? (1-5, before and after the session)
2. What was the most useful part? (open text)
3. What would you change? (open text)

Summarize the results (average confidence before vs. after, plus a few comments). If you run the session, that summary is a real result you can list on your resume. Until then, this is a plan, not completed training.
