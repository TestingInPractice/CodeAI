# GSD for OpenCode — полный обзор и демонстрация (стенограмма)

**Video:** https://www.youtube.com/watch?v=zRJ0UWHBjCY
**Author:** Владилен Минин (на английском)
**Date:** ~2025-07-26
**Language:** English (auto-generated)

---

[00:01] Hello,
[00:03] I'm going to talk about get [ __ ] done
[00:07] for open code. This very specific
[00:10] adaptation of the original get [ __ ] done
[00:15] uh le was
[00:18] designed by Tasher.
[00:22] uh his system right now is expanded to
[00:25] support not only cloud code but open
[00:27] code and even Gemini.
[00:30] Uh I tried it um I mean I tried it a lot
[00:34] but I tried that specific adaptation for
[00:37] open code and I
[00:40] didn't like it much. So I still believe
[00:43] that ours is
[00:46] much better for now. Uh that's why I
[00:50] will be using this very specific
[00:53] adaptation of that [ __ ] done for this
[00:56] very demonstration.
[01:00] Um, I'll try to I'll try to make
[01:02] everything as one shot and I'll probably
[01:05] will cut out of long executions or some
[01:09] poses or whatever is kind of
[01:13] unnecessary, some obstacles to
[01:16] understand the idea. So, don't be
[01:19] surprised to see that something is like
[01:22] too quick or okay, too quick. Anyways,
[01:26] so I assume that you have uh open code
[01:30] installed. So
[01:36] you have to execute one more command to
[01:40] install
[01:42] uh that GSD open code.
[01:45] Um I personally don't mind of course
[01:48] installing it into global uh set of
[01:52] config folders. Uh so I use uh one and
[01:58] there are several files like
[02:01] about 80 or 90 files that I installed uh
[02:06] into into this very
[02:09] uh into this very folder. So right now
[02:12] the system is already installed. So
[02:14] let's uh
[02:19] open the aentic code generation system
[02:23] open code and let's have a look. So the
[02:26] first the first thing of course
[02:29] uh to check I know help.
[02:34] So it's supposed to execute the yeah the
[02:40] prompt that shows a lot of useful
[02:43] information. So don't ignore it. There
[02:46] are really lots of useful
[02:49] information here. I don't know what is
[02:52] happening right now. It just worked
[02:56] pretty quickly
[02:58] before. Right. Okay. Let's Okay, it's
[03:03] happening internet and fluctuations.
[03:06] It's fine. It's fine.
[03:11] Uh [sighs]
[03:13] well, it's working.
[03:16] Well, it's working. I need to say that
[03:18] uh I've been using that uh Kimi
[03:22] car 2.5
[03:25] model for several days. So I'm using
[03:28] that one for like one day not not much
[03:31] but before I used original provider Kim
[03:36] uh so
[03:39] interesting if I if I uh yeah
[03:46] me for coding it's supposed to be
[03:48] working by the way I do have
[03:51] something
[03:53] help let's let's just kind of execute
[03:57] that one through another provider.
[04:03] Okay,
[04:05] I cannot say it's a lot better, but it's
[04:07] kind of better for my
[04:13] for my taste. Anyways, it's it's
[04:15] working. So it's by the way it's already
[04:18] consuming
[04:20] uh it's already consuming context
[04:25] and it even calculates the cost which is
[04:29] weird because I do have a subscription
[04:32] but anyways anyways
[04:37] doesn't really matter. So
[04:40] [clears throat] let me get back to the
[04:45] another provider just
[04:48] try to use that one. So first of all I
[04:51] need to show you that uh this
[04:55] folder is empty.
[05:05] Uh there is nothing here
[05:07] just no files no I nothing just just
[05:12] let's add
[05:14] subfolder with I don't know
[05:27] >> [snorts]
[05:30] >> again. Nothing is here. Let's open open
[05:34] code and start doing stuff.
[05:39] Uh by the way uh the usual workflow is
[05:44] uh described here in the readme file of
[05:47] the uh GSD open code and of course get
[05:51] [ __ ] done as well. Uh let's start with
[05:55] the very beginning. So
[06:00] we can skip that one. So let's start
[06:02] with a new project. So that command is
[06:06] supposed to be executed uh when you have
[06:09] an idea but you don't have any project
[06:11] any uh git repository uh initialized or
[06:16] like basically anything just empty empty
[06:19] fold.
[06:21] Uh let's execute that one. And while
[06:23] it's executing let's a little bit uh
[06:27] let's talk about what we're going to do.
[06:29] So this is uh an empty folder. I suppose
[06:35] we have an idea idea of like the
[06:38] beautiful application that you have in
[06:40] your mind. That application might be
[06:43] basically anything absolutely anything.
[06:46] It doesn't matter.
[06:49] Yeah. And by the way, it's asking asking
[06:51] about the kind of
[06:55] the application. So that is the place
[06:58] where you can put your ideas or your
[07:01] requirements or your vision or whatever
[07:04] you think there should be uh to be kind
[07:08] of to show you something solid. I will
[07:11] start with simple absolutely unnecessary
[07:15] tool that's I already already tried that
[07:18] before. So it worked. I know. Uh so
[07:20] let's kind of use Rust to create an
[07:24] application that kind of replicates uh
[07:28] replicates the uh functionality of the
[07:31] curl
[07:33] or something like that. So let's see.
[07:37] Um
[07:47] so
[07:49] that's a power of that prompt thing. So
[07:54] you don't have to define everything here
[07:57] because
[07:59] the prompt uh the kind of future prompts
[08:03] that are going to be executed uh they
[08:06] are um they will
[08:11] test if they understand the task
[08:14] completely or there are some gaps or
[08:17] uncover it or some kind of gray areas.
[08:20] So they will definitely get back to
[08:22] those areas and we'll ask questions
[08:24] about them. Uh so let's let's hit enter
[08:28] and okay. So what is going on next?
[08:34] Wonderful.
[08:36] Uh what features that make
[08:39] using cool?
[08:42] That's a good question because no there
[08:44] are not. [laughter]
[08:52] I don't know if it's okay or not.
[08:55] So you see that uh the prompt and the
[09:00] LLM
[09:02] uh kind of made assumptions and right
[09:05] now it is going to ask uh me questions
[09:09] about details. So that is the reason
[09:12] that is important part. So you don't
[09:14] have to define every detail because uh
[09:17] that thing is going to support you with
[09:20] all of the details that [snorts]
[09:24] um okay just get post let's
[09:28] okay let's choose that one.
[09:37] Uh what kind of colored output?
[09:44] Let's say all of above.
[09:52] What request custom?
[09:55] That's great. Uh
[10:00] lots of stuff actually. Okay, let's do I
[10:03] I didn't tweet much. So, let's say
[10:07] something like this. So, it doesn't
[10:09] matter. I just would like to create
[10:11] something which is working and then
[10:15] okay, better colorization. Yep. Better
[10:18] colorization.
[10:21] Uh
[10:23] okay. So we reached the point where the
[10:26] uh prompt and the llm
[10:29] are going to create a project file. The
[10:32] project that defines the entire project
[10:36] and then we are going to uh dive deeper
[10:40] into the details with the next with the
[10:43] next stages.
[10:45] So it might take some time.
[10:48] Uh my idea was and still is to create
[10:51] something that is possible to use within
[10:54] the same uh the same window just to show
[10:57] you the results. So like the results
[11:00] that we are going to achieve.
[11:03] I personally always use it yol thing
[11:07] because just why don't
[11:12] uh death let's do standard execution
[11:15] parallel of course get tracking um that
[11:19] is a good question that is a question
[11:20] about like um how to explain uh so
[11:24] during the process during the uh
[11:27] communications uh with the LLM LLM
[11:32] creates
[11:34] for you specific documents that are
[11:38] supposed to be a context.
[11:40] So all of like every detail that we
[11:44] discussed before will be put in some of
[11:46] the documents and those documents are
[11:48] going to be uh are going to be located
[11:51] in the
[11:55] okay
[11:56] all of the documents are going to be
[11:58] located in this very uh folder which is
[12:02] called planning and right now there is a
[12:06] only one document here project and in
[12:10] some situation you might kind of you
[12:13] might want to hide that information
[12:18] uh from the repository. So that question
[12:22] here is to to kind of to put that folder
[12:27] into the g ignore file and just never
[12:30] push it to the repository or uh uh
[12:36] support it. So use the same rules for
[12:39] like every file including the files
[12:41] located in that um
[12:45] in that dot
[12:49] uh planning folder files. So okay I I'll
[12:53] I'll use I I'll say yes. Uh for me it's
[12:56] crucial to have g backup those files.
[13:01] But you might think you might choose
[13:04] another option. That's your choice.
[13:07] What is next? Research before planning
[13:10] each phase. Yeah, of course. Of course.
[13:12] Better have a research. So, research is
[13:15] a super helpful thing. So when the LLM
[13:20] or the that system uh gets [ __ ] done is
[13:23] not sure about the results or not sure
[13:28] if it's possible to use some
[13:31] framework or library or approach
[13:35] it will perform the research. it will
[13:37] automatically get kind of get connected
[13:40] or reach out website with the
[13:42] documentation of the framework and we'll
[13:45] search for the necessary answers plan
[13:48] check it's another thing another useful
[13:50] thing so let's say yeah everything is
[13:53] yes and profile let's say quality
[13:58] uh that part is not kind of working any
[14:03] anyways
[14:06] it looks like everything is already
[14:07] done.
[14:11] Okay. Let's check let's check project.
[14:15] Okay.
[14:22] Yeah.
[14:26] Why it's planning? No. Please go ahead
[14:31] do some stuff.
[14:38] As you might see as you might notice uh
[14:42] that system started writing writing
[14:44] files into the specific folders.
[14:49] Uh what is happening right now the
[14:52] system is automatically
[14:56] uh involve invocated
[14:59] that GSD project researcher task. So
[15:03] that task is supposed to perform a
[15:05] research.
[15:08] Let's let's yeah let's have a look at
[15:10] the uh context
[15:15] uh limitations that are happening right
[15:19] now. So as you might notice the like the
[15:22] main uh flow is uh going on in this very
[15:27] window and you might kind of see here
[15:30] that we consumed already like 11 uh% of
[15:36] the context and that is okay. Nothing is
[15:38] wrong with that. Uh up to like 60% is
[15:42] kind of okay. If it's more, it might be
[15:47] a little bit less
[15:51] interesting. But anyway, so let me let
[15:53] me click I'm going to click on this very
[15:56] task. So it's a representation of the
[15:58] task which is happening
[16:00] um kind of behind. So if I go and click
[16:04] that task, you will see that we we have
[16:07] a different context window. So it's a
[16:09] different
[16:12] session with the LLM. So that session
[16:17] uses its own context and that is a huge
[16:23] advantage of this get [ __ ] done
[16:29] meta prompt system uh because it's uh
[16:32] it's kind of set up or designed to
[16:35] execute or involve different agents for
[16:38] different uh part of the task uh
[16:41] development.
[16:43] And each agent is supposed to be
[16:46] executing some specific part of the task
[16:49] within its own context. So the idea here
[16:53] is just to never reach
[16:56] uh the context window limit. So that is
[17:02] totally possible. That is totally and as
[17:05] far as I understand right now I cannot
[17:08] open that window like on a full screen
[17:11] because I'm kind of recording the screen
[17:14] right now but I can say that there are
[17:18] okay at least how many one two three
[17:22] four five
[17:26] different agents working
[17:31] I believe that one is already done
[17:33] right. So
[17:35] yeah, it looks like research is over.
[17:38] 23% by the way.
[17:42] And that one is still Yeah, that one is
[17:45] still doing something. 33%.
[17:50] It's okay.
[17:52] So
[17:54] you see that we actually
[17:57] uh defined our project with a very
[18:01] common kind of description. There were
[18:03] no details and later we answered some
[18:06] questions. The questions were
[18:09] okay. they were reasonable but they
[18:13] didn't cover everything of course and
[18:16] right now uh that system tries to fill
[18:20] the gaps
[18:22] and that is a advantage of that approach
[18:27] while it's doing that let's have a look
[18:29] at the
[18:32] at the uh description of the comments so
[18:37] you already uh saw that command. So
[18:41] right now we are executing that GSD new
[18:45] project command and that command is uh
[18:49] performing the initial process and this
[18:51] is exactly what is going on right now.
[18:54] After that is done we are going to work
[18:58] with the phases. So
[19:02] the idea here is not to dive into the
[19:08] production or dive into the development
[19:10] and generating the code immediately uh
[19:13] promptly from this very point. No. Uh
[19:17] the idea of the entire metaprompt system
[19:21] that gets you done is to separate
[19:27] a bigger task to a smaller
[19:29] >> [snorts]
[19:29] >> uh chunks or pieces and then work with
[19:33] each chunk separately
[19:36] and use the same approach.
[19:39] Use the same idea. So every chunk is
[19:42] supposed to be defined by you or by the
[19:46] system. You can ask the system literally
[19:49] what is your opinion something like by
[19:52] the way there is a
[19:55] yeah something like that and LM will
[20:00] analyze your application analyze a plan
[20:02] and will find important tasks that must
[20:05] be performed. So usually something that
[20:08] is something like uh okay let's let's
[20:11] generate additional jobs for the
[20:13] pipeline to perform some security
[20:16] testing or
[20:19] just a usual uh unit testing or I don't
[20:23] know a lot of a lot of stuff that is
[20:26] usually is kind of postponed until the
[20:29] last moment. No, that thing is
[20:33] much deeper in that regard.
[20:37] And sometimes it's it's even kind of
[20:40] surprising to see how deep the
[20:43] suggestions are. And again I I I like to
[20:48] repeat it kind of one more time. And
[20:50] just to remind
[20:53] it manages to
[20:56] uh separate tasks on a smaller chunks
[21:00] and then will use that chunk to kind of
[21:04] to fully devote itself all of these uh
[21:07] power to one specific task. And it will
[21:10] not start generating the code until the
[21:14] moment
[21:15] everybody including you [laughter]
[21:18] is fully aware of what is going on. What
[21:20] is going to be developing during that
[21:22] process during the next phase?
[21:32] Wow. Okay.
[21:37] Which core HTTP features are v1? I feel
[21:41] like I already answered those, but
[21:53] uh by the way, if you feel like
[21:55] something is missing during any request
[21:59] or any question, you can choose type
[22:02] your own answer
[22:04] and say, "Oh yes, everything
[22:09] call red perfectly.
[22:15] Uh
[22:17] you can you can write whatever you want.
[22:19] It's I mean if you feel like something
[22:22] is missing you can stop or request you
[22:27] know express your opinion in every
[22:29] moment and every screen it doesn't
[22:31] matter. It will be uh it will be uh used
[22:34] as part of the uh entire process.
[22:41] um create road map. Okay, it takes time.
[22:44] So the next thing Meta prompt system is
[22:47] going to do is a create file with the
[22:50] definition of the next steps.
[22:53] Not exactly detailed definition, but
[22:56] it's kind of visible what we'll we'll do
[23:00] first, second, third, and
[23:10] They are going to be located here.
[23:15] So yeah. So that is
[23:22] of course
[23:24] um let's
[23:29] I'm not of course reading that one. It's
[23:32] just some kind of definition of
[23:37] you see architecture features pitfalls.
[23:41] So all of these are results of the
[23:44] research and the like questionary that I
[23:48] answered before.
[23:51] So it's working. [laughter]
[23:54] That is that is great.
[23:58] Okay.
[24:02] Yeah, it it it it expects you to have a
[24:06] look at the files. Uh unfortunately or
[24:09] fortunately, it really depends on the
[24:10] point of view. Uh but I usually use I
[24:14] usually use a external editor just to
[24:17] check all the files. But right now it
[24:20] like let's let's pretend let's believe
[24:22] everything is perfect. I don't think it
[24:24] is, but who cares?
[24:29] So,
[24:34] yep, it's done. The project is
[24:36] initialized. All of the files are listed
[24:38] here. And the next thing that we are
[24:40] going to do is discuss
[24:44] discuss the next phase uh which is uh
[24:48] which is called or has number one
[24:51] uh just to be
[24:54] sure. So that is the next command here
[24:58] in the in the readme file. So
[25:04] let's do
[25:07] let's do the discussion stuff. So
[25:10] um technically I can just copy and paste
[25:15] that command into the prompt here and
[25:18] start executing it. But since like we
[25:21] already kind of uh created some context
[25:26] already executed something and that
[25:28] context is by the way 18%.
[25:32] So we can probably get rid of that. So
[25:36] let's do something like that. So yeah,
[25:38] we do have an empty context. And now I'm
[25:41] going to copy that
[25:44] discuss phase one. So let's let's do
[25:47] that.
[25:50] And as you might see, the system just
[25:53] started using the documents that were
[25:55] prepared previously.
[25:58] It started with empty memory of what
[26:02] happened like 3 minutes ago. Uh but it
[26:05] it quickly read all of the documents and
[26:08] now it is asking the questions.
[26:20] It is a not real application. I would
[26:22] spend much more time on thinking of the
[26:26] future uh uh features, but right now I'm
[26:29] just making my choices.
[26:34] Yeah, I'm I'm good. I'm good. Let's go.
[26:36] Go ahead. Just like let's create
[26:38] something.
[26:50] So remember that is the first phase. We
[26:53] are discussing the first phase. Actually
[26:58] we are covering some questions that are
[27:00] not clear from the previously like
[27:05] performed research and performed
[27:07] questions. So right now that system is
[27:11] going to create documentation about the
[27:17] yeah
[27:21] so let let me let me show you so in
[27:23] another window. So it created the phases
[27:27] folder and right now uh there is one
[27:30] phase and it's called like 01 core HTTP
[27:35] foundation and right now there is only
[27:38] one document which is called you see
[27:41] context like three kilobytes
[27:44] and the document is basically covering
[27:47] some of the
[27:49] details of the future application
[27:52] document that creates a context for the
[27:56] one phase and one phase only. Uh let me
[28:00] get back to the
[28:02] open code and you see there is uh there
[28:06] is again the same the same information.
[28:08] So uh get [ __ ] done recommends to
[28:13] execute a new command
[28:15] uh to get rid of the context that we
[28:19] already kind of created and consume it.
[28:21] it already transferring to LLM
[28:24] and then execute this plan phase. So the
[28:28] discussion is over
[28:30] [snorts] and let's plan the the first
[28:33] phase. So
[28:36] and then plan phase one.
[28:44] So right now I believe it's going to
[28:46] create a a sub agent. So subtask which
[28:51] is going to be executed in its own
[28:54] context and that subtask is going to
[28:58] plan like part of that phase because
[29:01] phases have stages right. So stages okay
[29:06] phase may consist of several
[29:10] steps
[29:11] right now there is nothing here.
[29:14] Okay,
[29:20] not quick enough to read all of that
[29:23] stuff, but I can see that. Okay, four
[29:27] plans. So, it decided to use four plans,
[29:30] four kind of subtasks or
[29:34] subphases of the phase one. I'll I'll
[29:38] I'll show you you'll see. So it's kind
[29:41] of it's a little bit okay sophisticated
[29:44] but not really. Let's switch to another
[29:48] window. So yeah that's what is
[29:51] happening.
[29:52] So you see that we are uh inside that
[29:59] phase one folder
[30:01] and right now it's the plan for the
[30:06] first phase first task is created or
[30:09] being created I don't know yet but it's
[30:12] it's working it's working and that is
[30:16] exactly what
[30:18] is expected
[30:20] created another file with the context
[30:23] for the second subtask for the first
[30:27] phase. So and the interesting idea uh
[30:31] behind that that it tries to create a
[30:36] plan which doesn't have any intersection
[30:39] with other plans.
[30:42] So you don't have to wait for one plan
[30:44] to be executed to be performed to start
[30:47] another one. And that makes it possible
[30:50] to execute all of these plans in
[30:53] parallel. So you don't have to wait. You
[30:57] just
[30:58] consume more tokens at the same time. So
[31:00] all of your plans will be executed in
[31:02] the parallel or not all but the plans
[31:06] that are kind of possible to execute in
[31:09] parallel will be executed in parallel.
[31:11] But you you you'll see. Hopefully,
[31:14] you'll see.
[31:23] You know, I I I just feel I'm feeling
[31:25] your emotions. [laughter]
[31:29] It's like that is boring.
[31:32] [laughter]
[31:34] Okay, I agree. But what can I do? So it
[31:39] it it it it will take some time. I will
[31:42] try to make it quicker. I mean the video
[31:45] itself but unfortunately yeah it takes
[31:49] time. Personally I don't know how to how
[31:52] to use Rust. [laughter] It's just
[31:57] I like to try. [laughter]
[32:00] So, um there might be some glitches or
[32:03] hiccups or whatever something
[32:07] that generated two more files. And by
[32:10] the way, the last one is a huge one like
[32:13] 21 kilobytes.
[32:15] Okay,
[32:18] it's a road map. So yeah, the
[32:21] interesting part of that technology that
[32:24] road map file and like all of the files
[32:27] actually in the uh in the root folder in
[32:30] the root planning folder are being
[32:33] updated from time to time
[32:36] uh because they should reflect the
[32:39] current status or current stage of the
[32:42] development process. So that is what
[32:45] going on. Okay. So
[32:48] dated palm breakdown wonderful. So the
[32:51] reason that's a record it's a sub agent.
[32:56] Uh it says that uh we can execute the
[33:00] first task of the first phase. Then uh
[33:04] we can execute two tasks in parallel and
[33:07] then uh the fourth uh task should be
[33:10] executed after the second and third. So,
[33:14] okay,
[33:17] I got back out of the sub agent
[33:22] and I believe it should finish updating
[33:27] the
[33:29] uh state files,
[33:33] road map files. So, like everything
[33:35] should be up to date and then after that
[33:37] it is going to
[33:41] uh yeah that's already here. So
[33:46] uh copy that command and then execute
[33:52] new to clear the context window and then
[33:57] execute that phase one.
[34:01] What is happening right now? This very
[34:04] root window um [snorts]
[34:07] kind of agent execution is going to uh
[34:10] read the current context take
[34:15] necessary stuff only necessary stuff and
[34:19] continue working on the tasks in the
[34:22] background. So I'm pretty sure it is
[34:25] going to
[34:27] uh I'm pretty sure it is going to start
[34:30] the sub agent for task one
[34:34] then wait for the task one to stop then
[34:38] execute task two and three in parallel.
[34:42] So there will be two sub aents working
[34:44] in parallel and then both of them are
[34:47] done. uh the fourth task is going to be
[34:50] execute that the only thing that I don't
[34:52] like right now and I believe that might
[34:54] be a mistake um
[34:57] that is not correct it's not supposed to
[35:00] be planner because planner has a
[35:03] specific approach so it's supposed to be
[35:06] built
[35:10] I didn't do anything I just
[35:14] [snorts]
[35:15] requested
[35:16] creation the application and then I just
[35:19] answered some questions and I didn't do
[35:22] anything at all. All of the researches,
[35:24] all of the decisions, all of the I don't
[35:27] know planning and
[35:29] necessary stuff was performed by that uh
[35:33] open code itself.
[35:36] And
[35:38] it's kind of great because
[35:42] if somebody would ask me to perform the
[35:44] same task just without any help from any
[35:47] AI system, I would like it would take me
[35:53] weeks
[35:55] at least days
[35:58] to start working on that stuff.
[36:03] If you ever tried, of course you tried
[36:06] to wipe code your own solution,
[36:08] application, script, whatever,
[36:11] everything that you put into context is
[36:14] super precious because you literally put
[36:17] some ideas into into your window
[36:21] uh is stored in that context. If you
[36:24] lose your window, you will lose a lot of
[36:27] work that you already put into like in
[36:30] your current session.
[36:32] Here in GSD,
[36:36] you don't care much. You can stop it at
[36:40] any moment. Of course, uh if you if I
[36:44] stop it right now, it will lose some of
[36:48] the results. So, right now, something is
[36:50] happening. It's definitely creating
[36:52] something or at least I hope it is.
[36:56] Let's check by the way. No, nothing is
[36:59] happening.
[37:07] Interesting.
[37:17] Okay.
[37:26] Nothing is happening. Okay. Okay.
[37:33] Restarted. Oh no. Spawn in formatting.
[37:36] So something is happening. At least
[37:39] something is happening. If we close that
[37:41] window and then reopen it and go back to
[37:44] the same uh to the same prompt and
[37:48] execute the same command just like the
[37:52] same GSD execute phase 01. It will start
[37:56] from this very point. Not from the very
[37:59] very beginning but from this very point
[38:02] because all of the results of the
[38:06] previous stages like all of the
[38:09] questions all of the decisions are
[38:11] already put in the correct context of uh
[38:14] of the like several files located in
[38:18] in the planning folder or the current
[38:22] folder. So that's the idea and
[38:30] so uh just as I mentioned before right
[38:33] now we are executing the first task of
[38:36] the first of the first phase and that is
[38:40] a wave one
[38:44] I hope
[38:47] I hope I'm pretty sure like the next
[38:49] step will be two two tasks are uh being
[38:53] executed uh in parallel because it was
[38:56] possible because it was just part of
[39:00] that
[39:02] part of that implementation part of that
[39:04] plan.
[39:08] Okay.
[39:12] Uh if we go into this sub agent session,
[39:15] you will see that yeah it's 20% because
[39:19] it uses its own context window
[39:23] and that context window will be
[39:26] abandoned just exactly at the moment
[39:29] that sub agent
[39:31] finished its work.
[39:34] It managed to create couple of commits
[39:39] in the uh g repository and right now
[39:43] what is happening right now is just like
[39:45] embarrassment uh because it's supposed
[39:48] to be working much faster.
[39:51] Unfortunately, it's not like that.
[39:54] However, I would like to bring your
[39:58] attention to the fact that there are two
[39:59] tasks right now that are going to be
[40:02] executed in parallel. This is another
[40:05] crucial point of that system. It
[40:08] executes the sub aents in parallel
[40:13] and more than that it tries to create
[40:17] the tasks in such a way that uh the
[40:21] tasks could be executed in parallel. So
[40:25] it is saying delegating but it is not
[40:29] because I haven't seen another task. So
[40:45] wow,
[40:50] there's a lot of work done here.
[40:54] Okay.
[41:06] Oh, what is that?
[41:10] I've seen something like that
[41:13] several times. And usually it mean it
[41:16] means that LLM wasn't kind of precise
[41:20] enough to uh execute a tool which is
[41:23] called right in this very example and it
[41:28] uh like executes that tool and the tool
[41:30] just expected something else some kind
[41:33] of like other format for the uh for the
[41:36] file or for the parameters and you yeah
[41:41] thinking I need to escape the context
[41:43] properly.
[41:44] Yeah, that is exactly what is usually
[41:46] happens uh uh when you use a
[41:51] let's say smartm because some of that
[41:55] smart especially locally running and
[41:58] they just like fails after after such an
[42:01] error. Uh that smart one is usually
[42:04] smart enough to like re-execute the same
[42:06] the same tool uh with a different set of
[42:10] parameters uh to make sure that
[42:15] that the file is created or whatever
[42:17] application was going to be performed
[42:20] like was really performed. So that is
[42:23] that is good. And by the way you see
[42:25] what is happening here is a update
[42:29] that system uh updates a file which is
[42:32] called state file and that file consist
[42:34] of that progress bar with like all of
[42:38] the necessary requirements and you see
[42:40] that we already reached two. So two out
[42:42] of 13 requirements are done and we are
[42:45] kind of 15%
[42:49] of the process.
[42:52] Actually, it's kind of consuming much
[42:55] more time than I personally expected to
[42:59] to spend on that video. I'm kind of I'm
[43:03] not sorry. [laughter]
[43:05] It's kind of it's even it's even, you
[43:08] know, it's even fun, [laughter]
[43:11] but I believe I believe that is super
[43:15] boring right now.
[43:20] Nobody's going to watch uh me talking
[43:22] about some weird stuff
[43:26] with my fake Russian accent
[43:28] [laughter]
[43:33] again. That is happening again.
[43:43] It performs some testing already.
[43:48] It's performing testing.
[43:53] Okay, it's doing something. It's
[43:54] verifying its own work. So, it actually
[43:59] checks the project against the
[44:07] uh checks the project against the
[44:10] specifications.
[44:12] So, your project must be on par with
[44:15] these specifications. I'm quite curious
[44:17] what is
[44:21] what will happen next. Will we have our
[44:26] working?
[44:28] Oh, it created the test and all of the
[44:32] tests are
[44:34] passed.
[44:38] So, it's basically testing the
[44:39] application against the specific sites.
[44:51] It's finishing. [clears throat]
[44:53] It's wrapping up the verification
[44:58] process. So, it's going to write the
[45:01] report. Yeah, it's already done.
[45:05] Yeah.
[45:10] So I believe we will have some something
[45:12] something to
[45:14] wow complete and verified. So it
[45:18] actually
[45:20] it's actually done
[45:26] not completely.
[45:29] Ah yeah it's supposed to yeah exactly
[45:31] it's supposed to update the uh file set
[45:35] allocated in the root root folder
[45:40] uh so requirements and the state and the
[45:45] road map like everything which is
[45:48] related to this.
[45:51] Uh yeah. So you see uh that is the set
[45:55] of requirements and that is what it
[46:00] updated
[46:02] and it
[46:04] marked the
[46:08] achieved results.
[46:15] Ah yeah it's done. Yeah. You see um I
[46:19] was I was slightly surprised. I was I I
[46:21] didn't expect to see something like this
[46:23] because usually uh every every execution
[46:27] stops and provides you with the uh kind
[46:31] of next steps what it is exactly to uh
[46:33] like what it is expected and what is the
[46:36] usual way uh to uh continue working. So
[46:40] uh just here I I'm not going to I'm not
[46:44] going to execute that command right now.
[46:46] But the idea here is just to execute
[46:49] again uh clear the uh context window and
[46:53] start discussing the next phase,
[46:57] gather some information uh some like me
[47:01] some decisions and that kind of stuff
[47:04] and then
[47:06] uh perform the next steps.
[47:09] However, what I'm going to do uh right
[47:13] now is just uh I'm going to oops, sorry.
[47:16] I'm going to copy
[47:19] hey
[47:25] some of the commands. I'm going to put
[47:28] that and then I'm going to exit and then
[47:35] since we are already here in this very
[47:39] folder I'm going to uh execute some of
[47:42] the commands.
[47:50] So that command is going to execute the
[47:53] utility we just created and uh uh
[47:57] perform get method on the uh
[48:02] this very
[48:05] this very
[48:10] J user age.
[48:14] here
[48:16] that's what that
[48:21] so return to us just I believe it's a
[48:25] wonderful wonderful utility good
[48:30] for debug
[48:33] yep
[48:41] well it works
[48:45] >> [sighs]
[48:46] [gasps]
[48:47] >> Okay, I believe that is okay for now. I
[48:51] will stop here in this very moment. It's
[48:54] too much. [laughter] I don't I don't
[48:57] know what to do. Uh maybe I was going to
[49:00] show how to deal with a debugger. uh how
[49:04] to how to fix uh how to fix errors if
[49:10] there were errors and that kind of
[49:13] stuff. But
[49:15] there were no errors and um but maybe
[49:19] later next video or
[49:22] I'll think about it.
[49:25] Uh happy coding. [laughter]
---

**↪️ 2025-07-26_GSD-for-OpenCode-thesis:** [[2025-07-26_GSD-for-OpenCode-thesis]]

**↪️ Категория:** [[README]]
