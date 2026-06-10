# GSD vs Paul: 7 проблем GSD и альтернатива (стенограмма)

**Video:** https://www.youtube.com/watch?v=MppKHh_MfFc
**Author:** (English, автор не указан в видео)
**Date:** ~2025-06-07
**Language:** English (auto-generated)
**Transcript:** YouTube auto-generated

---

[00:00] If you've been using Claude Code for the
[00:02] past month, you've heard and are
[00:04] probably using the Get Done plugin.
[00:06] But if for some reason you don't know
[00:08] about this plugin, go ahead and watch
[00:10] this video that I did about it a few
[00:12] weeks back. But there are some critical
[00:14] problems that I found using GSD for
[00:17] myself. And this new kid on the block,
[00:20] his name is Paul. does a lot of the same
[00:23] things as GSD, but actually solves seven
[00:27] critical problems that I've found using
[00:29] the tool. And to be clear, in this
[00:32] video, we're going to be talking from a
[00:34] complete non-technical perspective about
[00:36] the seven structural problems that Paul
[00:38] solves in comparison to GSD. Then we're
[00:41] going to head over to the terminal and
[00:42] I'm going to show you at a high level
[00:44] how to install and actually use Paul.
[00:46] Then we'll conclude with some final
[00:48] thoughts as to when you should use GSD
[00:50] versus Paul. When it comes to both of
[00:52] these plugins, one of the main things
[00:54] that they're trying to achieve is
[00:56] solving the context rod issue. The more
[00:59] that we chat in a context window, the
[01:01] worse the quality becomes. And in
[01:03] relation to that, the main architectural
[01:05] difference between GSD and Paul is that
[01:08] GSD is more of a relay race getting
[01:11] through phases, whereas Paul is a
[01:14] marathon. And this single decision
[01:16] between which plugin to use causes every
[01:19] problem that follows. So the first
[01:21] problem that Paul is going to solve is
[01:23] the knowledge transfer. There is a high
[01:25] token cost to reading all the notes
[01:28] every time we're starting a new phase as
[01:30] far as GSD goes. Looking at GSD, we're
[01:32] losing about 70% context from every
[01:35] different conversation or context window
[01:37] we're booting up versus pull where we're
[01:40] losing close to zero context. GSD in a
[01:43] sense is trading quality for freshness
[01:46] whereas Paul is going to trade the speed
[01:48] for continuity in the project
[01:50] development. Secondly, the loop is
[01:52] broken whenever we try to resume
[01:54] building a project in GSD. My input
[01:56] should not cause amnesia with the
[01:59] plug-in or or using claw code in
[02:01] general. With GSD, I move forward, we
[02:03] start something up, it pulls context,
[02:05] starts over again, and so on and so
[02:07] forth. With Paul, it's more of a
[02:09] marathon. And whenever we have a human
[02:11] interruption or some feedback, it's just
[02:13] going to keep proper continuity. In GSD,
[02:16] every interaction is going to trigger a
[02:18] full restart. So the current worker
[02:20] working on the project or the phase at
[02:22] hand will vanish. With Paul, it's just
[02:24] going to stay streamlined. The worker
[02:26] stays active. It takes the input and
[02:29] continues on straightforward. And third,
[02:32] fake verification. There is no guard
[02:34] rail with GSD that makes sure that the
[02:37] app is fully functional and working. And
[02:39] there's an acronym for this, UAT, user
[02:43] acceptance test, where we're actually
[02:45] making sure that the functionality is
[02:47] verified. And that's one thing that Paul
[02:50] does that GSD doesn't. So on one hand,
[02:53] GSD is going to build it, but on the
[02:55] other, Paul's going to build it slower
[02:58] with more continuity, but force you to
[03:00] make sure that all the APIs and all the
[03:03] different tech things and the tech stack
[03:05] is working and functionality is approved
[03:08] before we move on. Ultimately, GSD is
[03:11] checking file structure very static,
[03:13] whereas Paul runs a guided user
[03:16] acceptance test, a UAT. Problem four is
[03:19] that the room gets totally messy using
[03:22] GSD. We plan, we build, and the check is
[03:25] optional. Kind of like with problem
[03:26] three, and we end up with a lot of drift
[03:29] accumulation and a lot of hallucination
[03:31] with AI. And AI hallucination is
[03:33] basically where the AI goes off the
[03:35] walls and does something or says
[03:37] something completely not relevant to the
[03:39] actual product requirements when
[03:41] starting the project with our full
[03:43] description. With Paul, it's mandatory
[03:45] that we close out and organize
[03:47] everything before we finish the job. So,
[03:50] we're going to plan, build, and close
[03:52] out. Mandatory every single time.
[03:54] Without that mandatory cleanup, reality
[03:56] will drift from the initial
[03:58] documentation. Problem five, token cost.
[04:02] How expensive will each fix be when
[04:04] using GSD versus Paul? When you want to
[04:07] fix something using GSD, it uses all of
[04:09] its power and its might and you use up a
[04:12] lot of tokens when trying to fix
[04:14] something as small as a fly versus Paul.
[04:16] The response is scaled down
[04:19] proportionately to the fix that we're
[04:21] trying to make, saving us tons and tons
[04:23] of tokens. GSD is spinning up industrial
[04:27] style equipment to solve a problem that
[04:30] a simple fly swatter could fix and
[04:33] continues to fix it within continuity of
[04:35] your conversation with Claude. Now, this
[04:38] may be a problem to some and it may not
[04:39] be a problem depending on your use case
[04:41] and the type of app that you're trying
[04:43] to build, but GSD builds every phase and
[04:47] planning in parallel to one another.
[04:49] Whereas Paul is running everything one
[04:51] by one by one. With GSD, let's say we're
[04:55] working on phase one of the project and
[04:57] you have 1 A, 1 B, and 1 C. We have to
[05:01] make sure that none of the files in A,
[05:03] B, or C are connected to before or
[05:06] after. Otherwise, they could be working
[05:08] on the same file in conjunction and
[05:10] leading to integration failure. All is a
[05:13] single worker stream and we have that
[05:15] sequential processing 1 2 3 in place.
[05:18] He's slower but fully informed. stack
[05:21] that with the UAT, the user acceptance
[05:24] test, and quality is assured. And last
[05:27] but not least, to bring things full
[05:28] circle, we're dealing with silent drift.
[05:32] And what I mean by that is GSD is going
[05:35] to lead you sometimes into a silent
[05:37] drift where it's going to assume success
[05:40] with the build whereas Paul with the UAT
[05:44] testing it's going to validate the state
[05:46] of the project for you or have you and
[05:48] push you to do that every step of the
[05:51] way. And I'm not trying to push you away
[05:53] from using GSD. I think it's awesome. I
[05:56] think it was totally revolutionary when
[05:58] it first came out. Feels like I'm saying
[05:59] this like a year ago. It was only like a
[06:01] few weeks ago, but for independent
[06:04] tasks, building features that are
[06:06] unrelated, it totally excels. Massive
[06:09] scale. If you have 20 phases in a
[06:11] project where the orchestrator must stay
[06:14] light and we need to just kind of like
[06:15] build through things, it makes sense.
[06:18] And tooling maturity. So if we need
[06:20] access to a bunch of commands and a
[06:22] bunch of different things going on, it
[06:24] might be a better fit. So GSD is going
[06:26] to win on raw velocity and speed and
[06:30] parallelization, but Paul is more of a
[06:32] scalpel. He's going to be more granular
[06:34] with the build. So weigh your options.
[06:36] Take this as perspective, not advice or
[06:39] pushing you to do one thing or the
[06:40] other. And I went over a lot of this
[06:42] during the other slides, but you could
[06:44] take a look at this. Here's a comparison
[06:46] chart to understand the difference
[06:47] between GSD's speed versus pulse
[06:50] fidelity. So when deciding which plugin
[06:53] to use to build your project, it really
[06:56] comes down to choosing GSD for speed for
[07:00] independent work streams and massive
[07:02] scale versus choosing pole for quality
[07:05] scalpel like approach for production
[07:08] reliability and verifiable proofs. So
[07:11] now let's migrate into a highle
[07:13] technical look at what Paul does. And
[07:15] this is the repo. This is the command.
[07:18] So grab this command. come over to your
[07:21] terminal and run this command. You could
[07:23] just choose global and it's installed.
[07:26] Notice how we have a brand new folder
[07:28] here. And what we're going to do is
[07:29] we're going to open up Claude. And this
[07:31] is my alias for Claude. So now that
[07:34] we're active, the first thing you're
[07:35] going to want to do is run /paul in nit.
[07:40] And if some of you guys have seen my
[07:42] video on Carl, you can actually stack
[07:44] Carl with this and create custom domains
[07:47] within your Paul project. And me and my
[07:50] partner Chris, the creator of Paul and
[07:52] Carl, are actually working towards a
[07:54] full solution where it's an all-in-one
[07:57] app building plug-in that integrates
[07:59] Carl and Paul. And the main directive is
[08:02] to create SAS products. In any case,
[08:04] when I run the Paul initi, notice we get
[08:07] our Paul folder here. And I would
[08:09] suggest keeping it in plan mode first
[08:12] and discussing back and forth the type
[08:13] of project you want to create in the
[08:15] same way that you would use GSD so that
[08:17] we can create the file structure here.
[08:18] And since there is no claw MD, if you
[08:21] want to set up and run Carl and this
[08:23] individual project in place of the MD
[08:25] for separate knowledge domains, you
[08:27] could totally do that. Check out my
[08:29] video on Carl if you want to deep dive.
[08:30] Or you could just run up a regular
[08:33] claw.md file and reference another one
[08:35] that you might have already created. So
[08:37] now we're just creating the plan here
[08:39] that has some contacts. It's created the
[08:41] project MD and it has some tech choices
[08:43] here. So it's given me some choices and
[08:45] options and I can choose to decide what
[08:48] I'd like to do at this point. And I
[08:50] could just choose to accept the plan. So
[08:53] now it'll integrate and set everything
[08:54] up for me with my phases. And it's
[08:56] created the road map as well as the
[08:59] state MD for where we're at in
[09:01] development. And notice now after I
[09:03] cleared context and accepted
[09:04] permissions, it's actually created the
[09:06] canband board for me and it's having me
[09:08] test it. So it was pretty quick and I
[09:11] can test things out as I need. It's
[09:13] simple HTML. But basically the UAT and
[09:17] the one by one process of Paul is really
[09:19] powerful when you want to focus on
[09:21] quality. So again, this was just my
[09:24] perspective and what I've seen with GSD
[09:27] versus Paul. You can decide which one
[09:29] you want to use, but I wanted to at
[09:31] least give you guys the opportunity to
[09:33] try it out for yourselves. And for a lot
[09:35] of my builds, I don't need speed and I
[09:38] definitely don't need to use a million
[09:40] different tools all at the same time.
[09:42] So, I'm sticking with Paul from here on
[09:44] out, especially when it comes to client
[09:46] deliveries with my agency. We charge
[09:48] high ticket enough to the point where if
[09:50] I bring in a client, I can afford to
[09:52] spend a few weeks making sure that the
[09:54] app that I deliver is production ready.
[09:56] If you guys got some value out of this,
[09:58] consider liking the video and
[10:00] subscribing for more content like this.
[10:02] I do about two videos weekly on Claude
[10:04] Code workflows as well as plugins. And
[10:07] if you guys want to take it a step
[10:08] further, consider joining my school.
[10:11] It's in the description below. I have a
[10:13] lot of free Claude Code templates and
[10:15] guides in there. But I do have an
[10:16] optional upgrade for those of you who
[10:19] want to move up the premium or VIP. I do
[10:22] have an accelerated program within 90
[10:24] days. I guarantee that you will build
[10:26] your SAS application or agency and gain
[10:29] your first customer. And until March
[10:31] 2nd, the premium upgrade is 50% off. So,
[10:34] if you want to get in now, consider
[10:36] joining before the prices increase. I
[10:38] will be including access to
[10:40] subcontractors for your agency if you
[10:42] guys are looking to go that direction as
[10:44] a part of the premium upgrades, as well
[10:47] as access to some of our software builds
[10:49] that you guys can use as a base for your
[10:51] clients or your own individual projects.
[10:54] So again, I hope you guys enjoyed
[10:56] sitting here and watching and learning,
[10:57] and I hope to see you guys on the next
[10:59] one.
---

**↪️ 2025-06-07_GSD-vs-Paul-thesis:** [[2025-06-07_GSD-vs-Paul-thesis]]

**↪️ Категория:** [[README]]
