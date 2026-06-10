# GSD vs OpenSpec: сравнительный тест (стенограмма)

**Video:** https://www.youtube.com/watch?v=6FRk19CZSBY
**Language:** English

---

[00:00] I rebuilt
[00:00] one reasonably
[00:01] large app twice,
[00:03] first with GSD,
[00:04] then with OpenSpec,
[00:05] using the same
[00:06] brief, GPT-5.5
[00:08] with medium
[00:09] reasoning effort,
[00:10] and the same Codex
[00:11] CLI version.
[00:12] I expected a difference
[00:14] because these frameworks
[00:15] have different
[00:16] philosophies.
[00:17] I did not expect
[00:18] the numbers
[00:18] to look like this.
[00:20] OpenSpec finished
[00:21] in one hour
[00:21] and fifty-two minutes.
[00:23] GSD took
[00:24] six hours
[00:24] and forty-six
[00:25] minutes of elapsed time,
[00:27] including the abandoned
[00:28] Claude Code
[00:29] start and breaks.
[00:30] Even if I only count
[00:31] the successful Codex
[00:32] rerun,
[00:33] it still took
[00:34] five hours
[00:34] and twenty-five
[00:35] minutes of elapsed time.
[00:37] That is not active
[00:38] typing time.
[00:39] I took breaks, and GSD
[00:41] sometimes
[00:41] worked for long
[00:42] stretches on its own.
[00:44] I did not
[00:44] measure exact
[00:45] human minutes,
[00:46] so I will not pretend
[00:47] I did.
[00:48] At first
[00:49] I thought
[00:49] the usage screenshots
[00:50] would be
[00:51] the best evidence I had.
[00:52] Later,
[00:53] I parsed
[00:53] the local Codex logs,
[00:54] and the gap
[00:55] got even clearer.
[00:56] OpenSpec
[00:57] spent about
[00:58] thirty-five point
[00:58] three million tokens
[01:00] across six threads.
[01:01] GSD spent about
[01:03] one hundred twenty-six
[01:03] million tokens
[01:05] across thirty-eight
[01:06] threads.
[01:07] Based on the numbers,
[01:08] this should be simple:
[01:09] one tool was much faster
[01:11] and used far
[01:11] fewer tokens.
[01:13] Except the final repos
[01:14] made it complicated.
[01:15] From the browser,
[01:16] the two apps
[01:17] were surprisingly close.
[01:18] I could sign up, sign in,
[01:20] edit profiles,
[01:21] publish stories, post
[01:22] comments, send direct
[01:23] messages, check
[01:24] unread messages,
[01:25] and open the leaderboard.
[01:27] If I only
[01:28] judged the result
[01:29] by testing
[01:29] the UI in the browser,
[01:30] the faster tool
[01:31] would win right away.
[01:33] But when I opened
[01:34] the codebases
[01:35] and compared
[01:36] what was left behind,
[01:37] the slower run
[01:38] started making
[01:39] a better case for itself.
[01:40] Not through the UI,
[01:42] but through
[01:42] the project baseline.
[01:44] This is what this
[01:44] video is about.
[01:46] Both frameworks
[01:47] can generate a demo app.
[01:48] The more useful question
[01:49] is what you get
[01:50] in exchange
[01:51] for the extra process,
[01:52] and whether that
[01:53] exchange is worth it.
[02:00] GSD and OpenSpec are
[02:02] not tiny
[02:02] GitHub experiments
[02:04] in terms of attention.
[02:05] At the time of this test,
[02:06] GSD had fifty-nine point
[02:08] four thousand stars,
[02:10] and OpenSpec
[02:11] had forty-four point
[02:11] eight thousand.
[02:13] For a niche category
[02:14] like spec-driven
[02:15] development,
[02:15] that is a
[02:16] lot of attention.
[02:18] It makes the comparison
[02:19] more useful
[02:19] than reading two READMEs
[02:21] and picking
[02:21] the one
[02:22] that sounds nicer.
[02:23] I also did not
[02:24] want to test them
[02:25] on a toy app.
[02:26] A landing page,
[02:27] a todo list,
[02:28] or a small cat
[02:28] game can tell you
[02:29] whether the
[02:30] command works,
[02:31] but it does
[02:31] not really test
[02:32] the framework
[02:33] under pressure.
[02:34] The point of these tools
[02:35] is structure:
[02:36] requirements, planning,
[02:38] implementation,
[02:39] verification,
[02:39] follow-up changes.
[02:41] I needed something
[02:42] large enough
[02:42] to force the tool
[02:43] to manage
[02:44] many features at once.
[02:45] That project
[02:46] became NewWriter.
[02:48] The original version
[02:49] was a website
[02:50] I built with a friend
[02:51] in 2010.
[02:52] It ran on Drupal
[02:53] 6, which was already
[02:55] not exactly young
[02:56] by the time
[02:56] we were done with it,
[02:57] and over time
[02:58] it grew into a
[02:59] real community
[03:00] of writers.
[03:01] People came in, published
[03:02] stories, commented
[03:03] on each other's work,
[03:04] built profiles,
[03:05] sent messages,
[03:06] and generally did
[03:07] what communities do
[03:09] when they start existing
[03:10] without asking
[03:11] your permission first.
[03:12] Eventually,
[03:13] we had to shut it down.
[03:14] The site
[03:15] was Russian-speaking,
[03:16] the stack was
[03:17] badly outdated,
[03:18] and after the war
[03:19] started, pro-war
[03:20] opinions on the platform
[03:22] made the whole thing
[03:23] impossible to continue.
[03:24] I do not want to revive
[03:26] that community
[03:26] in that form, obviously.
[03:28] But the product
[03:29] idea itself
[03:30] stayed in my head
[03:31] for years:
[03:32] a clean, modern writing
[03:33] community, rebuilt
[03:34] from scratch
[03:35] on a modern stack.
[03:36] That made it a good test
[03:37] brief.
[03:38] The app needed
[03:39] authentication, writer
[03:40] profiles, avatars, story
[03:42] drafts and publishing,
[03:43] markdown rendering,
[03:45] categories, comments,
[03:46] direct messages,
[03:47] unread message counts,
[03:48] a leaderboard,
[03:49] a homepage,
[03:50] and seed data.
[03:51] Not enterprise software,
[03:53] but definitely
[03:54] more than a tiny
[03:55] demo app.
[03:56] That is the PRD
[03:57] I gave to
[03:57] both frameworks.
[03:59] Before the
[03:59] actual runs, here
[04:00] is a quick refresher
[04:02] on how these frameworks
[04:03] expect you to work.
[04:05] One small
[04:05] but important detail:
[04:07] command names
[04:07] depend on the host tool.
[04:09] In Claude
[04:10] Code, OpenSpec's
[04:11] current docs
[04:12] talk about OPSX
[04:13] commands
[04:13] like /opsx:propose.
[04:16] In Codex,
[04:17] at least in my project,
[04:18] the generated skills
[04:19] had not been renamed yet,
[04:20] so they showed up
[04:21] as $openspec-propose,
[04:24] $openspec-apply-change,
[04:26] and
[04:27] $openspec-archive-change.
[04:29] GSD is the heavier
[04:30] lifecycle framework.
[04:32] You start
[04:32] with $gsd-new-project,
[04:34] usually with --auto
[04:36] if you want it to read
[04:37] a PRD
[04:38] and make
[04:38] reasonable assumptions.
[04:40] That creates
[04:40] the planning state
[04:41] under .planning/:
[04:42] project notes,
[04:43] requirements,
[04:44] roadmap, research,
[04:46] phase folders,
[04:46] and the current
[04:47] state file.
[04:48] After that,
[04:49] the long flow goes
[04:50] phase by phase.
[04:51] You discuss
[04:52] the phase with
[04:52] $gsd-discuss-phase, plan
[04:56] it with $gsd-plan-phase,
[04:57] execute it
[04:59] with $gsd-execute-phase,
[05:00] verify it
[05:01] with $gsd-verify-work,
[05:01] and eventually
[05:02] ship it with $gsd-ship.
[05:04] There is also $gsd-next
[05:06] for detecting
[05:06] the next step,
[05:07] $gsd-autonomous
[05:08] for chaining
[05:09] more of the workflow,
[05:10] and $gsd-quick
[05:12] for focused fixes
[05:13] that should not become
[05:14] a whole project phase.
[05:16] GSD does
[05:17] more than write a spec
[05:18] and hand it to the model.
[05:19] It tries
[05:20] to run the whole project.
[05:21] It creates requirements,
[05:23] roadmaps, phase
[05:24] plans, research
[05:25] files, summaries,
[05:26] and verification
[05:27] artifacts.
[05:28] It can also
[05:29] use subagents,
[05:30] so different
[05:30] parts of the work happen
[05:32] in separate contexts.
[05:33] This is why I kept saying
[05:34] during the test
[05:35] that GSD feels like what
[05:37] BMAD should have been.
[05:38] There is process,
[05:39] but there is
[05:40] also automation
[05:41] behind the process.
[05:42] OpenSpec is much
[05:43] smaller conceptually.
[05:45] The core loop
[05:45] is $openspec-propose,
[05:47] $openspec-apply-change,
[05:48] and
[05:48] $openspec-archive-change.
[05:50] Propose creates
[05:51] a change folder
[05:52] with proposal.md,
[05:53] design.md, tasks.md,
[05:56] and delta specs.
[05:57] Apply works
[05:58] through the task list.
[05:59] Archive merges
[06:00] the delta specs
[06:01] into the canonical specs.
[06:03] For a small change,
[06:04] that is basically
[06:05] the whole flow.
[06:06] For a larger
[06:07] app, OpenSpec
[06:08] does not naturally create
[06:09] the full project roadmap
[06:10] for you in the same way
[06:12] GSD does.
[06:13] You split the app
[06:14] into several changes,
[06:15] then apply them
[06:16] one by one.
[06:17] That gives you less
[06:18] orchestration, fewer
[06:19] artifacts to manage,
[06:20] and less time
[06:21] waiting for the framework
[06:22] to decide
[06:23] what the project is.
[06:24] The shortest version is
[06:26] this:
[06:26] GSD wants to own
[06:28] the project.
[06:29] OpenSpec
[06:29] wants to own the change.
[06:31] Quick pause
[06:31] before we get into
[06:33] the actual runs.
[06:34] If you like
[06:34] this kind of practical
[06:35] AI coding test,
[06:37] subscribe to the channel.
[06:38] I am trying to make
[06:39] these comparisons
[06:40] useful instead of
[06:41] just reading
[06:42] product pages
[06:42] back at you.
[06:43] And if you want
[06:44] to talk to me
[06:45] or other community
[06:46] members, join
[06:47] the Discord.
[06:47] It is still small,
[06:48] but that also means
[06:50] it is actually possible
[06:51] to have a conversation
[06:52] there.
[06:52] The link is in
[06:53] the description.
[06:55] The GSD run
[06:56] started in Claude Code,
[06:57] and honestly,
[06:58] that first attempt
[06:59] made GSD
[07:00] look better
[07:01] as a framework.
[07:02] It asked more
[07:03] setup questions.
[07:04] It used subagents
[07:05] on its own.
[07:06] The whole thing
[07:07] looked closer to
[07:08] the architecture GSD
[07:09] was designed around.
[07:11] The main context stayed
[07:12] focused on orchestration.
[07:14] Specialized agents
[07:15] handled research,
[07:16] planning, execution,
[07:17] and verification.
[07:19] The framework
[07:19] kept state in .planning/.
[07:21] The problem
[07:22] was not the workflow.
[07:23] The problem was limits.
[07:24] I was on
[07:25] the one-hundred-dollar
[07:26] Claude Max plan.
[07:27] That had been enough
[07:28] for serious
[07:29] coding before,
[07:30] but I had worked
[07:31] heavily that week,
[07:31] so the weekly
[07:32] limits were
[07:33] already drained.
[07:34] A subagent-heavy GSD
[07:35] run was not something
[07:37] I could comfortably
[07:37] finish there anymore.
[07:39] At the same time,
[07:40] Codex
[07:40] had a promo running
[07:41] through the end
[07:42] of May 2026
[07:43] with double usage
[07:44] on the one-hundred-dollar
[07:46] Pro tier.
[07:47] After June,
[07:47] that means the
[07:48] available usage
[07:49] should drop back
[07:50] to roughly half of what
[07:51] I had during this test.
[07:53] But for this
[07:53] test, Codex
[07:54] was the practical place
[07:55] to finish.
[07:56] So after about an hour
[07:58] and twenty minutes,
[07:58] I restarted from scratch
[08:00] in Codex.
[08:01] That first attempt
[08:02] was not wasted.
[08:03] By then,
[08:04] I understood
[08:04] the GSD process
[08:05] much better.
[08:06] But it still showed
[08:07] something important
[08:08] about this
[08:09] test: GSD's
[08:10] preferred architecture
[08:11] can become expensive
[08:13] when the host tool
[08:14] has tight limits.
[08:15] In Codex,
[08:16] the project completed.
[08:17] It went through the major
[08:18] phases: foundation
[08:19] and auth, profiles
[08:20] and story
[08:21] publishing,
[08:22] public discovery
[08:22] and comments, messages
[08:24] and leaderboard,
[08:25] then seed
[08:25] data and final polish.
[08:27] The final app had
[08:28] the expected surface
[08:29] area from my manual
[08:31] acceptance pass:
[08:32] sign-up, sign-in,
[08:33] profiles,
[08:34] avatars, drafts,
[08:35] publishing, markdown,
[08:36] categories, comments,
[08:38] direct messages, unread
[08:39] badge, leaderboard,
[08:40] homepage, and seeded
[08:42] demo data.
[08:43] The run was
[08:44] still not smooth.
[08:45] Codex did not
[08:46] use subagents
[08:47] as naturally as Claude
[08:48] Code did,
[08:49] so I had to explicitly
[08:50] tell it
[08:51] that agents were allowed.
[08:52] Context management
[08:53] mattered in a very
[08:54] practical way:
[08:55] fresh sessions
[08:56] helped,
[08:57] and I had to verify
[08:58] the app
[08:59] after phases
[08:59] instead of
[09:00] assuming the plan meant
[09:01] the result was correct.
[09:03] Several times
[09:04] GSD disappeared
[09:05] into a long phase
[09:06] while I waited
[09:06] for the stop sound
[09:07] and came back later
[09:09] to review the result.
[09:10] That last part is
[09:11] where GSD
[09:12] is much better than BMAD,
[09:13] at least for me.
[09:14] I do not like slow
[09:15] human-in-the-loop
[09:16] workflows where
[09:17] agents mostly
[09:18] pretend to be different
[09:19] roles.
[09:20] One acts like a PM,
[09:21] another acts
[09:22] like a planner,
[09:23] and my job is to read
[09:24] a long document
[09:25] and press a button.
[09:26] GSD can run in auto mode
[09:28] and do a meaningful
[09:29] chunk of work
[09:30] while you step away.
[09:31] Set a sound
[09:32] when the turn is done,
[09:33] come back, review
[09:34] the result.
[09:35] That is a workflow
[09:36] I can live with.
[09:37] The cost is that
[09:38] these chunks are large
[09:39] and slow.
[09:40] OpenSpec iterations
[09:41] were much faster.
[09:42] GSD felt more autonomous
[09:44] and more disciplined,
[09:45] but slower to adjust.
[09:47] The upside
[09:47] is that GSD left behind
[09:49] the stronger repo.
[09:50] It had test,
[09:51] typecheck, lint, build,
[09:53] and prisma:generate
[09:54] scripts.
[09:55] It had four
[09:55] actual test files.
[09:57] It used DATABASE_URL
[09:58] instead of hard-coding
[09:59] the SQLite path.
[10:01] It had cleaner
[10:02] helper separation
[10:03] in a few places,
[10:04] and the avatar upload
[10:06] path used a better
[10:07] filename strategy
[10:08] instead of leaning
[10:09] on the original filename.
[10:11] So the GSD
[10:12] story is not slow
[10:13] and bad.
[10:14] It is slow, heavy,
[10:15] and technically
[10:16] more serious
[10:17] than the browser result
[10:18] alone would suggest.
[10:19] The OpenSpec run
[10:21] felt simpler
[10:21] from the moment
[10:22] the integration
[10:23] was in place.
[10:24] Installation itself
[10:25] should be straightforward
[10:26] for a normal setup.
[10:28] Install the package
[10:29] globally, run openspec
[10:30] init, select Codex,
[10:31] and it creates
[10:32] the OpenSpec
[10:33] folder plus
[10:34] the generated skills.
[10:36] The small
[10:36] install friction
[10:37] I hit came from my local
[10:38] Mac user setup,
[10:40] not from OpenSpec itself,
[10:41] so I would not hold that
[10:42] against the framework.
[10:44] In this project,
[10:45] the Codex skills
[10:46] showed up
[10:46] as $openspec-propose,
[10:48] $openspec-apply-change,
[10:49] $openspec-archive-change,
[10:51] and $openspec-explore.
[10:53] That is
[10:53] slightly confusing
[10:54] because the
[10:55] current Claude
[10:55] Code docs
[10:56] talk about OPSX
[10:57] commands like
[10:59] /opsx:propose,
[11:00] but for the actual
[11:02] Codex run,
[11:02] these were the names
[11:03] I used.
[11:04] The workflow
[11:05] itself was simple.
[11:06] OpenSpec creates
[11:07] a change folder
[11:08] with proposal.md,
[11:10] design.md, tasks.md,
[11:12] and delta specs.
[11:13] Then Codex applies
[11:15] the change,
[11:15] you check the result,
[11:16] archive it, and move on.
[11:18] For a project
[11:19] this size,
[11:20] the cleanest approach
[11:21] would probably be
[11:22] to ask an LLM
[11:23] to split the app
[11:24] into phases first.
[11:25] That plan
[11:26] could live outside
[11:27] the framework
[11:27] as a small markdown file,
[11:29] and then each phase
[11:30] could become its own
[11:31] OpenSpec change.
[11:33] I did not do that
[11:34] upfront.
[11:34] Instead,
[11:35] I prompted OpenSpec
[11:36] to implement
[11:37] the first phase,
[11:37] and during that planning
[11:39] and implementation
[11:40] flow, it
[11:40] created three
[11:41] additional proposals
[11:42] for the remaining work.
[11:44] So when
[11:44] phase one was done,
[11:45] I already had the next
[11:47] three changes proposed
[11:48] and ready to apply.
[11:49] That helped,
[11:50] but I still felt
[11:51] more responsible
[11:52] for steering the roadmap
[11:53] than I did with GSD.
[11:55] The first foundation
[11:56] change produced
[11:57] a runnable
[11:58] app at localhost 3000
[12:00] with authentication,
[12:01] Prisma, SQLite, seed
[12:02] data, public pages,
[12:04] categories, profiles,
[12:05] and follow-up
[12:06] changes prepared.
[12:07] Some features were
[12:08] still stubs,
[12:09] but the app looked
[12:10] real much earlier
[12:12] than I expected
[12:13] because there was already
[12:14] a browser-visible
[12:15] product,
[12:15] instead of only planning
[12:17] files.
[12:18] The later changes
[12:19] filled in the rest:
[12:20] profile editing,
[12:21] avatars, story
[12:22] authoring, comments,
[12:23] private messages,
[12:24] unread message
[12:25] counts, leaderboard,
[12:26] homepage blocks,
[12:27] and final acceptance.
[12:29] The final acceptance
[12:30] pass used Playwright,
[12:31] found small issues
[12:32] like favicon
[12:33] and narrow-screen
[12:34] layout bugs,
[12:35] and fixed them.
[12:36] OpenSpec was weaker
[12:37] on the repo baseline.
[12:39] The app worked,
[12:40] but compared with GSD
[12:41] it left less engineering
[12:43] scaffolding behind.
[12:44] There was no test script,
[12:45] no typecheck script.
[12:47] The Prisma
[12:48] setup hard-coded
[12:49] the SQLite path
[12:50] despite
[12:51] having an .env.example,
[12:53] and some logic lived
[12:54] more directly inside
[12:55] routes and actions.
[12:56] Nothing catastrophic,
[12:58] but if I had to continue
[12:59] one of these repos
[13:00] tomorrow,
[13:01] I would trust the GSD
[13:02] baseline more.
[13:03] OpenSpec felt fast,
[13:04] lean, and easy to steer
[13:06] because the loop stayed
[13:07] small:
[13:08] propose, apply,
[13:09] check, archive,
[13:10] then prompt
[13:11] the next change.
[13:12] The strange part
[13:13] is that the visible
[13:14] apps were much closer
[13:15] than the workflows.
[13:17] By the end,
[13:17] both implementations
[13:18] had the core
[13:19] NewWriter features.
[13:20] They had sign-up
[13:21] and sign-in,
[13:22] profiles, avatars, story
[13:24] drafts, publishing,
[13:25] markdown rendering,
[13:26] categories, comments,
[13:27] direct messages,
[13:28] unread message
[13:28] counts, leaderboard,
[13:29] homepage blocks,
[13:31] and seeded demo data.
[13:33] If I opened the two
[13:34] apps in the browser
[13:35] and tested
[13:35] the main user flow,
[13:37] the difference was not
[13:37] dramatic enough
[13:38] to explain the time gap
[13:40] by itself.
[13:41] The problems
[13:41] were similar too,
[13:43] which matters.
[13:44] Both frameworks
[13:44] missed form
[13:45] preservation at first.
[13:47] If a login
[13:47] or sign-up failed,
[13:48] the app did not keep
[13:50] the entered values
[13:51] in the way I expected.
[13:52] Both also had awkward
[13:54] comment behavior
[13:55] after posting:
[13:56] the comment existed,
[13:57] but the page
[13:58] did not reveal
[13:59] the new comment cleanly,
[14:00] so the result was easy
[14:02] to miss.
[14:02] The unread message badge
[14:04] was a slightly
[14:05] different case.
[14:06] I did not explicitly
[14:07] put it in the spec,
[14:08] but once
[14:09] direct messages existed,
[14:10] it felt obvious
[14:11] that the navigation
[14:12] should show
[14:13] unread messages.
[14:14] Both versions
[14:15] needed a follow-up
[14:16] for that.
[14:17] There were also bigger
[14:18] production concerns that
[14:19] go beyond this
[14:20] comparison.
[14:21] Avatar upload
[14:22] validation
[14:23] was not something
[14:23] I would call
[14:24] fully production-safe,
[14:25] and neither app
[14:27] had serious captcha
[14:28] or abuse protection.
[14:29] I do not treat that
[14:30] as a framework failure,
[14:32] because this was outside
[14:33] the realistic scope
[14:34] of a single generated
[14:36] comparison run.
[14:37] For a real public
[14:38] writer community,
[14:39] I would
[14:39] probably outsource
[14:40] authentication
[14:41] and user management
[14:42] to a proper
[14:43] third-party service
[14:44] instead of pretending
[14:45] this is a small feature.
[14:47] It costs money,
[14:48] but auth is a huge thing
[14:49] to build
[14:50] and maintain properly.
[14:52] I would not call that
[14:53] a framework failure.
[14:54] This was a lot of app
[14:55] surface for one
[14:56] generated run,
[14:57] and the observed
[14:58] UI issues are fixable
[14:59] through prompts.
[15:00] My read
[15:01] is that some of this came
[15:03] from the brief,
[15:03] the model,
[15:04] and the product
[15:05] complexity, with GSD
[15:06] and OpenSpec
[15:07] only being part
[15:08] of the story.
[15:09] So when I compare them,
[15:11] I do not think the
[15:12] main question is
[15:13] which one generated fewer
[15:14] UI bugs?
[15:15] The answer is not
[15:16] clean enough
[15:17] to be useful.
[15:18] The better question
[15:19] is: after
[15:20] the bugs are fixed,
[15:21] what kind of workflow did
[15:22] I have to go through,
[15:24] and what kind of repo
[15:25] was left behind?
[15:26] This is where I am going
[15:27] to put the scorecards
[15:29] on the screen.
[15:29] I rated both frameworks
[15:31] with the same evaluation
[15:32] categories:
[15:33] spec quality,
[15:34] plan quality,
[15:35] implementation quality,
[15:36] first result, polish
[15:37] cost, cost, developer
[15:39] experience, adaptability,
[15:41] and verification
[15:41] discipline.
[15:42] These are judgment
[15:43] scores from this run,
[15:45] not a universal
[15:46] benchmark.
[15:46] The category table is
[15:48] what makes this
[15:48] score auditable.
[15:50] The final number
[15:51] by itself is not enough.
[15:52] GSD landed at seven point
[15:54] five out of ten.
[15:55] OpenSpec landed
[15:56] at eight out of ten.
[15:58] That score might
[15:59] look strange
[16:00] if you only heard
[16:01] the part
[16:01] about repo quality.
[16:03] GSD scored
[16:04] higher on spec quality,
[16:05] planning, implementation
[16:06] quality, adaptability,
[16:08] and verification
[16:09] discipline.
[16:10] It produced better
[16:11] planning artifacts.
[16:12] It had a real quick flow.
[16:14] It left behind
[16:15] tests and typecheck.
[16:16] It looked more
[16:17] like a framework
[16:18] that wanted to protect me
[16:19] from sloppy engineering.
[16:20] OpenSpec scored higher
[16:22] where the
[16:22] day-to-day experience
[16:24] was better:
[16:24] first result, polish
[16:26] cost, cost,
[16:27] and developer experience.
[16:28] It got to a convincing
[16:29] app much faster, used
[16:31] fewer moving parts,
[16:32] and kept the feedback
[16:34] loop short enough
[16:35] that I did not
[16:36] feel trapped
[16:36] in the workflow.
[16:37] The token table
[16:38] makes the cost difference
[16:40] very visible.
[16:41] From the parsed Codex
[16:42] logs, GSD spent one
[16:43] hundred twenty-six
[16:44] point zero
[16:45] million tokens
[16:46] across thirty-eight
[16:47] threads.
[16:48] OpenSpec
[16:49] spent thirty-five point
[16:50] three million across
[16:52] six threads.
[16:53] GSD spent about
[16:54] ninety point
[16:54] seven million
[16:55] more tokens,
[16:56] or roughly
[16:57] three point
[16:58] five seven times as many.
[17:00] Using GPT-5.5 API
[17:02] pricing from May 2, 2026
[17:04] as an estimate,
[17:05] and counting cached
[17:06] input separately,
[17:07] GSD comes out to
[17:09] about one hundred
[17:10] three dollars
[17:10] and ninety-nine
[17:11] cents API-equivalent.
[17:13] OpenSpec comes out to
[17:15] about twenty-seven
[17:15] dollars
[17:16] and seventy-one cents.
[17:17] Reasoning tokens
[17:18] are included
[17:19] in the output-token
[17:20] bucket in these logs,
[17:21] So I am not
[17:22] counting them twice.
[17:23] That was not
[17:24] my actual bill.
[17:25] I was lucky enough
[17:26] to get the Codex
[17:27] promo code,
[17:28] so I ran this for free
[17:29] under
[17:29] promotional subscription
[17:31] limits.
[17:31] Those limits
[17:32] are doubled only
[17:33] until the end
[17:34] of May 2026,
[17:36] and starting
[17:36] from June 2026,
[17:38] they should drop back
[17:39] to roughly
[17:40] half of what I had
[17:41] during this test.
[17:42] The dollar numbers
[17:43] are only there to compare
[17:44] the token
[17:45] spend in a more
[17:46] familiar way.
[17:47] The quota
[17:47] screenshots point
[17:49] in the same direction,
[17:50] but the logs are better
[17:51] evidence.
[17:52] GSD was much heavier.
[17:54] OpenSpec
[17:54] was much cheaper to run.
[17:56] GSD made a stronger case
[17:58] for code quality
[17:59] because it left behind
[18:00] tests, typecheck,
[18:01] better configuration,
[18:03] and cleaner
[18:03] project scaffolding.
[18:05] My personal choice
[18:06] for this kind of work
[18:07] would be OpenSpec.
[18:08] That does not
[18:09] make OpenSpec the better
[18:10] framework in every sense.
[18:12] It is not.
[18:13] GSD produced
[18:14] the stronger repo.
[18:15] If you care about quality
[18:16] checks, verification,
[18:17] and letting the
[18:18] framework manage
[18:19] more of the engineering
[18:20] process,
[18:21] GSD has a real argument.
[18:23] It is much closer
[18:24] to what I wanted
[18:25] BMAD to be:
[18:26] structured, autonomous,
[18:27] and capable
[18:28] of doing work
[18:29] instead of asking me
[18:30] to approve
[18:30] more documents.
[18:31] But for my own
[18:32] working style,
[18:33] OpenSpec
[18:34] is easier to live with.
[18:36] I like fast iterations.
[18:37] I like being able
[18:38] to prompt, check, adjust,
[18:40] archive, and move on.
[18:41] I do not want every
[18:42] small correction
[18:43] to become
[18:44] a large process.
[18:45] OpenSpec gave me that.
[18:46] It was fast enough
[18:47] that I stayed engaged
[18:49] with the work,
[18:49] instead of mentally
[18:50] switching away
[18:51] for half an hour
[18:52] and coming back
[18:53] to inspect
[18:53] whatever happened.
[18:54] GSD is better
[18:55] when you want bigger
[18:56] autonomous chunks.
[18:58] Set it running,
[18:59] wait for the sound, come
[19:00] back, review the result.
[19:01] That is a valid workflow,
[19:03] and for some people
[19:04] it will be better.
[19:05] Less technical builders
[19:06] might prefer it
[19:07] because the
[19:08] framework owns
[19:09] more of the planning
[19:09] and verification.
[19:11] Teams
[19:11] evaluating these tools
[19:12] might also care
[19:13] more about the stronger
[19:14] repo baseline
[19:15] than about my
[19:16] personal impatience.
[19:18] And I should be fair
[19:19] to GSD here.
[19:20] This test
[19:21] still felt like
[19:22] it covered
[19:23] only a small part
[19:24] of the framework.
[19:25] It has advanced features
[19:26] and configuration
[19:27] options underneath that
[19:28] I did not
[19:29] properly explore
[19:30] in this comparison.
[19:31] So if you want
[19:32] a dedicated GSD video,
[19:34] let me know
[19:34] in the comments.
[19:35] There is clearly more
[19:36] there than
[19:37] one side-by-side
[19:38] build can cover.
[19:39] By the way,
[19:40] I am also very curious
[19:41] how both frameworks
[19:42] would behave
[19:43] with something
[19:43] like Composer 2 Fast.
[19:45] Composer 2 is very fast,
[19:46] so the whole process
[19:47] would probably
[19:48] feel snappier,
[19:49] even with GSD.
[19:51] Maybe GSD would not feel
[19:52] nearly as slow
[19:53] in that setup.
[19:54] A lot of this comparison
[19:55] is GSD versus OpenSpec
[19:57] through a specific stack:
[19:58] the framework,
[19:59] the coding tool,
[20:00] the model, and the limits
[20:01] all working together.
[20:03] Change one
[20:03] part of that stack,
[20:04] and the tradeoff
[20:05] can move.
[20:06] So the practical
[20:07] recommendation is simple.
[20:08] If you can own the
[20:09] roadmap yourself
[20:10] and you want speed,
[20:12] start with OpenSpec.
[20:13] If you want the framework
[20:14] to manage
[20:15] more of the process,
[20:16] and you are willing
[20:17] to spend more time
[20:18] and tokens
[20:19] for better quality
[20:20] gates, try GSD.
[20:21] I pushed both
[20:22] generated repos publicly,
[20:24] so you can check them
[20:25] yourself.
[20:25] The links are
[20:26] in the description
[20:27] and on screen.
[20:28] And for the
[20:29] final benchmark,
[20:30] my cat would obviously
[20:31] choose OpenSpec.
[20:32] Once she requests dinner,
[20:34] she does not expect
[20:35] a five-phase
[20:36] execution plan
[20:37] while the bowl
[20:38] is being prepared.
[20:39] She expects the result
[20:40] immediately.
[20:42] Faster is better,
[20:43] and frankly,
[20:43] her acceptance testing
[20:44] is harsher than mine.
---

**↪️ 2025-07-26_GSD-vs-OpenSpec-thesis:** [[2025-07-26_GSD-vs-OpenSpec-thesis]]

**↪️ Категория:** [[README]]
