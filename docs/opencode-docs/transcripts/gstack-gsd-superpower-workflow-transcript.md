# GStack + GSD + Superpowers Workflow — Полная стенограмма

**Видео:** https://www.youtube.com/watch?v=BlTpG51x94w  
**Канал:** Spectrum Development  
**Тема:** Обзор трёх фреймворков (Superpower, GStack, GSD) и их комбинация в единый workflow + Ralph Loop для полной автономии

## Структура видео

```
1. Введение — что такое spectrum development и зачем комбинировать фреймворки
2. Обзор трёх фреймворков:
   - Superpower → test-driven development, написание тестов до реализации
   - GStack → role-based brainstorming (CEO, Designer, Eng Manager, Security)
   - GSD → борьба с context rot, удержание под 50% контекстного окна
3. Комбинированный workflow: GStack → GSD → Superpower
4. Ralph Loop (Build Loop) — полностью автономное исполнение
5. Live demo: 16 фаз, 100+ headless-сессий, 10% контекста
```

## Полная стенограмма

Spectrum development здесь helps AI здесь to plan things before doing implementation. And on this channel we have reviewed tons of spectrum of frameworks. So that's why in this video we're going to take a look at the most popular spectrum development frameworks that we have like Superpower, GStack, GSD, and we're going to take a look at how we can piece them all together into a single workflow that we're going to use to building applications with the highest accuracy. And most importantly, we're going to take this one step further. We're going to introducing the route loop here to see how we can be able to build this applications completely autonomous. Or we're going to have Clocko here to using Clocko headless where I can spin up different iterations and each iteration here can be able to call like Superpower, GStack, GSD, and all the scales, all the MCP servers that we have and try to having it orchestrator here to loop through until we have the project is fully built. So we can do this completely autonomous using the route loop approach and also achieve the highest accuracy extract by extracting all the best skills from each frameworks and pieces all together into our own workflows.

So pretty much that's what we're going to cover in this video and if you're interested, let's get into the video.

Now before we continue, I recently launched our school community where I help you to master AI agents, automations, and so much more. And that's all coming from someone who used to work as a senior AI software engineer at companies like Amazon and Microsoft. And in this community, you're going to get over 100 plus video materials like templates and workflows that I personally built and sold over 100 plus times. On top of that, you also going to get access to our weekly live calls. And just give you an idea, this week we're actually running a Clocko masterclass where we're going to dive into how to improve Clocko's accuracy when we're going to use it to building applications. Plus you're also going to get full community supports where you're going to get chance to ask questions and get direct answers back. So if you're ready to level up, make sure you drop right in and I'll see you in the community.

All right, so in order to understand how we can be able to piece all those workflows together, let's understand what spectrum development does, right? So for spectrum development here, it basically help you to or help AI here to plan things before doing executions and we all know that. But essentially, this is the workflow that most spectrum development here follows. It doesn't matter if it's spec kit, the B map method, or you know, any other XYZ framework. They always go with something like brainstorming, right? Helping you to clarify what you're trying to build. Then it's going to go down to like planning, right? How exactly we're going to execute this? Maybe a task list, or maybe breaking this task into different phases, and each phase has its own task list. And then eventually it's going to go down to executions, and eventually here has review, has verifications, maybe having using Playwright here to spin up another browser agent here to verify everything, right? So, you can see that this is the entire spectrum of workflows that pretty much most frameworks here follows.

And essentially, how each framework here different is that for Superpower here, like you can see for each one, what's special about each one is that for Superpower, it's really good at focusing on test-driven developments, which is something that other workflow doesn't have. It's focusing on writing test first before it do the implementation.

And then for GStack, it's a little different. It also follow that framework, but the selling point here for GStack is that it's focusing on role-based, which has like different CEO, designers, engineer managers, or maybe security manager here, try to integrate with different personalities here, try to help you to decide a best decision for your product, right? Maybe you're still in the planning phase, or maybe brainstorming phase, it's going to help you to dive deep and try to help you to identify that, right?

And furthermore, we also have GSD, which it will help us to avoid context rot. And just to give you a quick TLDR what the context rot means, if you have ever interact with large language model, usually it will start to become pretty accurate before 50% of the context window, right? Maybe after you surpass like 50% of the context, it will start to become lower for the accuracy, right? That's exactly what context rot means, is that the more you talk to the AI in the same context, the lower the accuracy it start become. And that's exactly what GSD is trying to solve, is that to make sure that each time when you interact with Claude code or any other coding agents, it's going to make sure that you stay under 50% for the context window. And that's exactly what GSD does.

And you can see that with all the special power listed from each frameworks, we can now be able to take the best out of each frameworks and try to piece it together into our own spectral framework that will help you to build applications here much more accurate, right? So, that's exactly how I would do it to take the best out of all three and try to place it into the right workflow.

So, you can see that this is the exact workflow that I use. **I use GStack here to do better brainstorming for clarify my intent** on exactly what I'm building because that's what GStack is really good for. And I'll basically put this for the planning phase. And then once we have our spec down, once we are using GStack here to clarify our intent, create our spec, then we're using **GSD here to basically taking our spec and break it down into different phases**. And the reason why we do this is like I said, the context rot issue, right? We don't want to put the entire spec into Claude Code and have it to execute everything. We want to break it down into different phases. And each phase will guarantee Claude Code here is going to stay under 50% and that's it. And this will give us the highest accuracy when we delegate each phase to the Claude headless or Claude session to do the execution.

And eventually here you can see after we break it down into different phases, we're going to using **Superpower here to follow test-driven developments** here to doing the execution for each phase. And that's exactly how I would do it if you were to want to achieve the highest accuracy when building applications using this approach.

Now, maybe for some of you guys, this will be like a really overkill because it's huge, right? Let's say if you're going to building something from scratch — a large application — I would definitely highly highly recommend you go with this approach, especially for a greenfield project, not a brownfield project. If it is a brownfield project, I'll highly recommend go with one or the other, right? For example, using Superpower here to adding additional feature or maybe using GStack plus Superpower here to building a larger or like a semi-large projects. But if you're going from a greenfield project, then I'll highly recommend you to go with this approach.

And you can see here that because this is going to break it down into different phases. And let's say if there's like eight or seven phases, then you have to pass the prompts continuously starting a new session to do it all over again, right? That's going to be really time taking. **And that's why I built a skill called Build Loop using the power of Ralph Loop here to basically do this autonomously**, which means that if I were to break all the phases — break the spec into different phases — and each phase has its own prompt. And we can be able to use that and store all those prompts into a single state or single file.

So for example, we have our Build Loop here, which will basically trigger and it's going to look through our states on exactly what are the phases that has completed. Then it's going to complete the one that's not completed and basically by delegating that phase into a headless session.

So the basically the way how it works here is that we — if we were to do `claude -p`, it's going to do this in a Claude headless way. Which for example, if I were to interact with Claude Code, I usually do something like this, right? And this will start a Claude Code session and I can be able to start interacting with this approach. But if I don't want to do this, I want to have like Claude here to run in a terminal, for example, I can do the `claude -p`. So if I were to do the `-p` and I give the exact prompt — for example if I were to do like "what is one plus one" — it will basically run in the background and it will basically try to execute that prompt and that's it.

And the good thing about this is that I can still run the main Claude Code session as this is like the orchestrator. And the orchestrator here can still run in this command, right? Inside of the orchestration to basically have it to be like this is going to be the one in the phase one. So if I were to do like `claude -p` and just the prompt say like "Hey, execute the phase one", it's going to do that. After it's done, it's going to respond it just like how we responded to for the answer for one plus one, it's going to give us the answer here. Once it gives us the answer, it's going to do the next command which is the `claude -p` for phase two, right? It's going to do this for iteration after iterations until everything's are all complete.

And like I said, the benefits of doing this is that we can have our orchestrator here to basically doing the phase by phase, right? For example, the orchestrator here is going to delegate task to a background job, try to process phase one, and is not going to take any context in the main orchestrator. The only thing that it takes is the headless session. It's going to run in the background. After it has completed the job in the background, it's going to exit, it's going to give you the outputs for the results for the summary, and then it's going to split it back into phase two and try to pass it to a new Claude session in the background and try to execute.

So you can see that this way approach is going to give us the most highest accuracy because the Claude orchestrator here doesn't take any context for the exact work. The only thing that it does is to delegate it into sub background job here to do so.

And for each background job here or each background Claude session here, it's basically going to, using like Superpower or GStack, try to execute those one by one, right? And if you want to take a step deeper on exactly how each background session is going to work — you can see that we have our Superpower here. So basically we're using Superpower here for executions. And usually what it does here is that it may go through like planning, dispatching agents, following test-driven development here, and eventually going to do review and verifications.

And you can see that for Superpower here, if there's any times where there's like decision being made, what we can do here is that usually it will basically try to trigger back to the orchestrator and try to ask those questions. And what we can do is we can be able to actually delegate this task. For let's say if there's any design questions, we can delegate this to GStack and have GStack here to trigger like different personality here to answer the questions. For example, if they like design patterns, we can trigger the GStack here to basically pass these questions to like different roles like CEO, engineer manager, or designers, and try to have them to vote on exactly what option they want. And at the end of it, it's just going to take the most popular vote and coming back to the main flow and try to continue on going forward.

So this way you can see that we're not going to have any manual involvement, we're just going to have each Claude headless session here to basically try to do the executions and have it to make its own decisions along the way. And that's basically how it works.

**So the architecture at the bottom level:**
- **GStack** is there for making decision if there's any questions
- **Superpower** is the backbone for the execution
- **GSD** handles phase decomposition

**At the upper level:**
- **Work scheduler** delegates task to each headless session
- Each headless session has its own **fresh context window**
- **Ralph Loop** iterates until completion

And the way how we have these phases here is we're using GSD to break them into different phases. And each phase has its own prompt, its own workflow to basically do executions. And eventually here you can see we're also using GStack here to basically create a spec. And that's where these phases here are coming from, which is from the spec that we have using the GStack here to clarify our intent and break our requirement into different phases.

**Let me show you some of the results that I have getting using this approach.**

Finally, just to show you a live demo, here you can see that we have the entire build queue is all completed. So I basically spun up a Claude session in this terminal and have it to run Build Loop overnight. And you can see that we have one session, which is the current session that we're in, which is the orchestrator, and it has completed over 100 sessions in the background. So it spun up Claude headless and try to complete phase by phase over in the background and try to get everything completed.

And you can see that the overall project here is **16 phases out of 16 is all completed**. And you can see we have the entire build queue here is all empty. The entire spec is now codified. And if you were to scroll all the way down for the context, so for the context window, **we only have spent 10% of it**. And that's why we delegate all the tasks into different headless sessions to basically complete the job for us. And we're keeping all the things that we have in the current session here clean and simple.

And that's exactly how they work. We take the specials from all the frameworks that we have like:
- **Test-driven developments** from Superpower
- **Different rules for making better decisions** from GStack
- **Avoiding context rot** from GSD

And eventually piece them all together into a single workflow that we can follow to have a highest accuracy for building applications following spectrum developments. And eventually we can be able to make this completely autonomous so they can be able to build it by itself overnight using the power of Ralph Loop to do this completely autonomous.

## Ключевые понятия

| Термин | Описание |
|--------|---------|
| **Spectrum Development** | Подход, при котором AI планирует перед выполнением. Общий пайплайн: brainstorming → planning → execution → review/verification |
| **Superpower** | Фреймворк, специализирующийся на test-driven development — тесты пишутся до реализации |
| **GStack** | Role-based brainstorming — разные личности (CEO, Designer, Eng Manager, Security) голосуют за архитектурные решения |
| **GSD (Get Shit Done)** | Фреймворк для борьбы с context rot — разбиение спеков на фазы, каждая < 50% контекстного окна |
| **Context Rot** | Деградация точности модели при заполнении контекстного окна > 50% |
| **Ralph Loop (Build Loop)** | Оркестратор, который делегирует фазы в headless Claude-сессии и итерирует до завершения |
| **Headless Session** | Фоновая Claude-сессия (`claude -p`), выполняющая одну фазу с чистым контекстом |

## Архитектура комбинированного workflow

```
                    ┌─────────────────────────┐
                    │   GStack (Spec Creation)  │
                    │   Brainstorm + Clarify    │
                    │   Role-Based Voting       │
                    └──────────┬──────────────┘
                               │ spec
                    ┌──────────▼──────────────┐
                    │   GSD (Phase Decomp)     │
                    │   Break spec into phases │
                    │   Each phase < 50% ctx   │
                    └──────────┬──────────────┘
                               │ phases[1..N]
                    ┌──────────▼──────────────┐
                    │  Ralph Loop (Orchestrator)│
                    │  Delegates to headless    │
                    │  sessions sequentially    │
                    └──────────┬──────────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
     ┌────────▼───┐  ┌────────▼───┐  ┌────────▼───┐
     │ Headless #1 │  │ Headless #2 │  │ Headless #N │
     │  Superpower │  │  Superpower │  │  Superpower │
     │  TDD cycle  │  │  TDD cycle  │  │  TDD cycle  │
     │              │  │              │  │              │
     │  Questions?  │  │  Questions?  │  │  Questions?  │
     │  → GStack    │  │  → GStack    │  │  → GStack    │
     └──────────────┘  └──────────────┘  └──────────────┘
```

## Результаты из демо

- **16 фаз** из 16 completed
- **100+ headless-сессий** выполнено в фоне
- **10% контекста** использовано в оркестраторе
- Полностью автономная сборка overnight
