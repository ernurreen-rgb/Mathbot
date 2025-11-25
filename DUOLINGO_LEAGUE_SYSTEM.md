# Duolingo League System

## Core Purpose and Motivation

The Duolingo League System is a gamification feature designed to:

- **Increase User Engagement**: Encourage daily practice through competitive motivation
- **Boost Retention**: Create a weekly commitment cycle that brings users back regularly
- **Drive Learning Through Competition**: Leverage social comparison and achievement psychology
- **Reward Consistency**: Recognize users who maintain regular practice habits
- **Create Community**: Foster a sense of belonging through shared competitive experiences

Users earn **XP (Experience Points)** by completing lessons, practicing skills, and engaging with various learning activities. This XP drives their rank within their league, creating a continuous motivation loop.

## Weekly Cycle and Group Formation

### League Start and Reset
- **Weekly Duration**: Each league competition runs for exactly **7 days**
- **Start Time**: New leagues begin every **Monday at midnight** (local time)
- **Reset Mechanism**: At the end of each week (Sunday at 11:59 PM), rankings are finalized and users are promoted, retained, or demoted

### Dynamic Group Formation
- **Group Size**: Each league consists of mini-groups of approximately **30-50 random users**
- **Random Assignment**: Users are matched with others who are active at similar times, creating fair competition
- **Group Activation**: Users **join a league group only after completing their first activity of the week**
  - This prevents inactive users from occupying spots
  - Ensures all competitors are actively participating
- **Continuous Formation**: As existing groups fill up (reaching capacity), **new groups are automatically created**
- **Isolation**: Each group competes independently; users only compete against members of their specific group

### Join Timing Strategy
The delayed group assignment (after first weekly activity) means:
- Early-week starters may face different competition than late-week joiners
- Strategic users sometimes delay their first lesson to join potentially easier groups
- The system balances fairness with encouraging early and consistent engagement

## XP and Ranking Mechanics

### Earning XP
Users accumulate XP through various activities:
- **Completing Lessons**: Primary source of XP (typically 10-20 XP per lesson)
- **Practice Sessions**: Reviewing previously learned material
- **Stories and Podcasts**: Engaging with supplementary content
- **XP Boosts**: Temporary multipliers available through in-app purchases or achievements
- **Perfect Lessons**: Bonus XP for completing lessons without mistakes

### Ranking Determination
- **XP Total**: Your rank within your league group is determined **solely by total XP earned that week**
- **Tiebreakers**: In case of equal XP, the user who reached that total first ranks higher
- **Real-Time Updates**: Rankings update continuously throughout the week as users earn XP
- **Leaderboard Visibility**: Users can see their current position and XP gap to adjacent competitors

## Promotion, Retention, and Demotion Zones

At the end of each weekly cycle, users are sorted into three zones based on their final ranking:

### 🏆 Promotion Zone (Top Performers)
- **Positions**: Typically the **top 7-10 users** in the group
- **Outcome**: **Advance to the next higher league** (if not already in Diamond League)
- **Indicator**: Green or gold highlighting in the leaderboard
- **Reward**: Achievement badges and advancement to more competitive tiers

### 🔄 Retention Zone (Middle Tier)
- **Positions**: The **middle majority** of the group (positions ~11-40)
- **Outcome**: **Remain in the same league** for the next week
- **Indicator**: Standard/neutral highlighting
- **Implication**: Consistent but not exceptional performance

### 📉 Demotion Zone (Bottom Performers)
- **Positions**: The **bottom 5-10 users** in the group
- **Outcome**: **Drop to the next lower league** (if not already in the lowest tier)
- **Indicator**: Red or warning highlighting in the leaderboard
- **Motivation**: Creates urgency to avoid relegation, even if promotion seems unlikely

**Note**: Exact zone sizes may vary slightly based on group size and total active participants.

## League Tiers: Complete Progression System

Duolingo features **10 distinct league tiers**, ordered from lowest to highest:

### 1. 🪨 **Bronze League**
- **Entry Level**: All new users start here
- **Difficulty**: Lowest competitive intensity
- **No Demotion**: Cannot drop below Bronze
- **Purpose**: Introduction to the league system

### 2. 🥈 **Silver League**
- **Rank**: 2nd tier
- **Difficulty**: Slightly more competitive than Bronze
- **Typical XP Range**: 200-500 XP to promote

### 3. 🥇 **Gold League**
- **Rank**: 3rd tier
- **Difficulty**: Moderate competition begins
- **Typical XP Range**: 400-800 XP to promote

### 4. 💎 **Sapphire League**
- **Rank**: 4th tier
- **Difficulty**: Above average competition
- **Milestone**: Entering advanced leagues

### 5. 💚 **Ruby League**
- **Rank**: 5th tier
- **Difficulty**: Consistently high performers
- **Typical XP Range**: 800-1500 XP to promote

### 6. 💜 **Emerald League**
- **Rank**: 6th tier
- **Difficulty**: Serious competitive environment
- **Typical XP Range**: 1200-2000 XP to promote

### 7. 🔮 **Amethyst League**
- **Rank**: 7th tier
- **Difficulty**: Very high competition
- **Achievement**: Indicates dedicated learner status

### 8. 🍀 **Pearl League**
- **Rank**: 8th tier
- **Difficulty**: Elite tier competition
- **Typical XP Range**: 2000-3500 XP to promote

### 9. 🔥 **Obsidian League**
- **Rank**: 9th tier
- **Difficulty**: Near-maximum competitive intensity
- **Achievement**: Reserved for most committed users

### 10. 💠 **Diamond League**
- **Rank**: **Highest tier**
- **Difficulty**: **Maximum competitive intensity**
- **Unique Characteristics**:
  - **No Further Promotion**: Diamond is the pinnacle; users cannot advance higher
  - **No Demotion**: Most implementations prevent demotion from Diamond to preserve achievement
  - **Competition for #1**: The primary goal shifts to finishing **#1 in your Diamond group**
  - **Top 3 Recognition**: Finishing in the top 3 often grants special badges or recognition
  - **Prestige**: Represents the most dedicated and consistent learners in the Duolingo community
  - **Weekly Challenge**: Each week brings a new group, renewing the competition for the #1 spot

### Progression Summary
```
Bronze → Silver → Gold → Sapphire → Ruby → Emerald → Amethyst → Pearl → Obsidian → Diamond
  ↑                                                                                    ↑
Starting                                                                          Pinnacle
Point                                                                            (No further
(Cannot                                                                          promotion)
demote)
```

## Key Design Principles

1. **Accessibility**: Everyone starts at Bronze, ensuring an entry point for all skill levels
2. **Graduated Difficulty**: Each tier requires progressively more XP and dedication
3. **Achievement Recognition**: Reaching higher leagues provides intrinsic and social rewards
4. **Sustainable Competition**: Weekly resets prevent burnout while maintaining engagement
5. **Peak Experience**: Diamond League represents mastery and ongoing excellence
6. **No Penalty for Reaching Top**: Diamond users won't lose their status, reducing anxiety about maintaining position

## Strategic Implications

- **Early Consistency**: Users benefit from starting lessons early in the week to establish position
- **XP Planning**: Competitive users plan daily XP targets to stay in promotion zones
- **Diamond Maintenance**: Once in Diamond, the pressure shifts from promotion to weekly ranking
- **Comeback Potential**: Demotion allows users to rebuild confidence and climb again
- **Social Dynamics**: Leagues create shared experiences discussed in communities

---

This system combines behavioral psychology, game design, and social motivation to create one of the most effective retention mechanisms in educational technology.
