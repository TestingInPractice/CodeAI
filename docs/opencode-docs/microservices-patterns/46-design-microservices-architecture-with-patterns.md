# Design Microservices Architecture with Patterns & Principles

## Overview

**Repo:** [mehmetozkaya/Design-Microservices-Architecture-with-Patterns-Principles](https://github.com/mehmetozkaya/Design-Microservices-Architecture-with-Patterns-Principles) (462 ★)  
**By:** Mehmet Ozkaya  
**What it is:** A step-by-step evolution of an e-commerce system from a simple monolith to a full event-driven microservices architecture, demonstrating 30+ design patterns and principles across 11 incremental stages. Built with C# (.NET 9), ASP.NET Core, and .NET Aspire.

## Architecture Evolution (11 Steps)

Each step introduces a new architecture pattern and adds non-functional requirements (scale, availability, latency, resilience).

```
Step  1: Monolith (Blazor + InMemory)
Step  2: Monolith + PostgreSQL
Step  3: Separated API Service + WebApp
Step  4: Modular Monolith (Domain Modules)
Step  5: Modular Monolith + Redis Cache
Step  6: Full Microservices (Polyglot Persistence)
Step  7: Microservices + Sync HTTP Communication
Step  8: Microservices + YARP API Gateway
Step  9: Event-Driven Microservices (RabbitMQ + MassTransit)
Step 10: Hybrid Cache (in-process + Redis) + Multi-Replica
Step 11: Outbox Pattern for Reliable Messaging
```

### Step 1: Monolithic One App

**What:** Single ASP.NET Core Blazor Server app with EF Core InMemory database. Everything in one process.

```
User Browser  <-->  Blazor Server App
                         |
                    EF Core InMemory (EShopDb)
```

**Patterns:** Monolithic Architecture, 3-Tier (implicit)  
**Stack:** C# .NET 9, Blazor Server, EF Core InMemory, .NET Aspire

---

### Step 2: Monolith + PostgreSQL

**What:** Replaces InMemory with PostgreSQL via .NET Aspire container management.

```
User Browser  <-->  Blazor Server App
                         |
                    EF Core PostgreSQL
```

**Patterns:** Database per Application, Infrastructure as Code (Aspire)  
**Stack:** PostgreSQL, EF Core Migrations, Aspire AppHost (`AddPostgres`, `WithPgAdmin`)  
**Change from Step 1:** InMemory → PostgreSQL with migrations

---

### Step 3: Monolith + Separate UI

**What:** Splits into two processes: `ApiService` (ASP.NET Core Web API) + `WebApp` (Blazor Server frontend) communicating over HTTP.

```
User Browser  <-->  WebApp  <--HTTP-->  ApiService
                                              |
                                         PostgreSQL
```

**Patterns:** Client-Server Separation, Service Abstraction Layer  
**Stack:** HttpClient, Aspire Service Discovery  
**Change from Step 2:** Single process → two processes over HTTP

---

### Step 4: Modular Monolith

**What:** Refactors the ApiService into domain modules (Catalog, Basket, Ordering) as separate projects with clear DDD boundaries, but still one deployment.

```
ApiService (Modular Monolith)
     |
 +---+---+---+
 |   |   |   |
Catalog Basket Ordering
Module  Module  Module
 |      |      |
Postgres Postgres Postgres
```

**Patterns:** Modular Monolith, Domain-Driven Design, Vertical Slice Architecture, Shared Kernel  
**Change from Step 3:** Code organized into bounded-context modules with `AddXModule`/`UseXModule` registration pattern

---

### Step 5: Modular Monolith + Redis Cache

**What:** Adds Redis distributed cache for basket data. `RequestSender` project added for load testing.

**Patterns:** Distributed Caching, Cache-Aside  
**Stack:** Redis (`Aspire.StackExchange.Redis.DistributedCaching`), RequestSender  
**Change from Step 4:** Redis cache + performance testing tool

---

### Step 6: First Microservices Split

**What:** Modules extracted into independently deployable microservices with polyglot persistence.

```
WebApp
 |
 +-------+-------+
 |       |       |
Catalog Basket  Ordering
 |       |       |
Postgres Redis  SQL Server
```

**Patterns:** Microservices Architecture, Database per Service, Polyglot Persistence, Service Discovery  
**Stack:** Catalog → PostgreSQL, Basket → Redis, Ordering → SQL Server  
**Change from Step 5:** Class library modules → separate Web API projects, each with own database technology

---

### Step 7: Synchronous Communication

**What:** Explicit sync HTTP calls between services — Basket calls Catalog (price validation) and Ordering (checkout).

**Patterns:** Synchronous Inter-Service Communication, Chained Service Calls  
**Stack:** HTTP Clients with Aspire service discovery  
**Change from Step 6:** `basket.WithReference(catalog).WaitFor(catalog)` — Basket depends on Catalog

---

### Step 8: YARP API Gateway

**What:** Introduces YARP Reverse Proxy between WebApp and services. Gateway handles routing, rate limiting, URL transforms.

```
WebApp  <--HTTP-->  YARP API Gateway
                      |
          +-----------+-----------+
          |           |           |
       Catalog     Basket      Ordering
      (80% req)  (15% req)   (5% req, rate-limited)
```

**Patterns:** API Gateway, Reverse Proxy, Rate Limiting, Backend for Frontend (BFF)  
**Stack:** `Yarp.ReverseProxy`, `Microsoft.Extensions.ServiceDiscovery.Yarp`, `Microsoft.AspNetCore.RateLimiting`  
**Change from Step 7:** WebApp calls gateway instead of services directly; rate limiting on Ordering (5 req/10s)

---

### Step 9: Event-Driven with RabbitMQ

**What:** Replaces sync HTTP calls with async events via RabbitMQ/MassTransit. `Shared.Messaging` project for event contracts.

```
WebApp  <--HTTP-->  YARP API Gateway
                      |
          +-----------+-----------+
          |           |           |
       Catalog     Basket      Ordering
          |           |           |
          +-- RabbitMQ Message Bus --+
    (ProductPriceChanged)   (BasketCheckoutIntegrationEvent)
```

**Patterns:** Event-Driven Architecture, Message Broker, Publish-Subscribe, Integration Events, Eventual Consistency, Loose Coupling via Events  
**Stack:** RabbitMQ (Aspire `AddRabbitMQ`), MassTransit, `Shared.Messaging` with `IntegrationEvent` base class  
**Change from Step 8:** Services communicate via events instead of sync HTTP; no direct endpoint coupling

---

### Step 10: Hybrid Cache + Multi-Replica

**What:** Basket gets its own PostgreSQL database + HybridCache (in-process + Redis layered cache). Scaled to 3 replicas.

**Patterns:** Hybrid Caching (local + distributed), CQRS with Caching, Multi-Replica Deployment, Cache Invalidation  
**Stack:** `Microsoft.Extensions.Caching.Hybrid`, `HybridCacheEntryOptions` (`Expiration`, `LocalCacheExpiration`, `DisableLocalCache`), `WithReplicas(3)`  
**Change from Step 9:** Basket has its own PostgreSQL (was only Redis); HybridCache for fast local reads + Redis fallback; 3 replicas

---

### Step 11: Outbox Pattern

**What:** Ordering writes order + outbox message in the same database transaction. Background process reads outbox and publishes to RabbitMQ. Guarantees at-least-once delivery.

```
Ordering Service
     |
  Write Order + OutboxMessage (same DB transaction)
     |
  Background Outbox Processor
     |
  RabbitMQ (reliable publish)
```

**Patterns:** Outbox Pattern, Transactional Message Sending, At-Least-Once Delivery, Idempotent Consumer (implied)  
**Stack:** EF Core outbox table, background processor  
**Change from Step 10:** Order writes and outbox writes in same transaction; prevents message loss on crash

## Technology Stack

| Layer | Technology |
|-------|-----------|
| **Language** | C# (.NET 9) |
| **Web Framework** | ASP.NET Core Minimal APIs, Blazor Server |
| **Orchestration** | .NET Aspire AppHost (container management) |
| **Databases** | PostgreSQL, SQL Server, InMemory |
| **Caching** | Redis (StackExchange.Redis), HybridCache |
| **Messaging** | RabbitMQ, MassTransit |
| **API Gateway** | YARP Reverse Proxy |
| **Rate Limiting** | ASP.NET Core built-in |
| **Service Discovery** | Aspire Service Discovery |
| **Containerization** | Docker (via Aspire) |

## Complete Pattern Map

| # | Step | Patterns Introduced |
|---|------|-------------------|
| 1 | Monolith | Monolithic Architecture, 3-Tier |
| 2 | Monolith + DB | Database per Application |
| 3 | Separate UI | Client-Server, Service Abstraction |
| 4 | Modular Monolith | DDD Bounded Contexts, Vertical Slices, Shared Kernel |
| 5 | Cache | Distributed Caching, Cache-Aside |
| 6 | Microservices | Database per Service, Polyglot Persistence |
| 7 | Sync Calls | Synchronous Communication, Service Chaining |
| 8 | API Gateway | API Gateway, Reverse Proxy, Rate Limiting, BFF |
| 9 | Event-Driven | Event-Driven Architecture, Pub/Sub, Eventual Consistency |
| 10 | Hybrid Cache | Hybrid Caching, Multi-Replica, Cache Invalidation |
| 11 | Outbox | Transactional Outbox, At-Least-Once Delivery |

## Non-Functional Requirements Evolution

```
Step 1-3:  Low request volume, single user
Step 4-5:  Growing volume, need for modularity
Step 6-7:  Independent scaling, polyglot persistence
Step 8:    Centralized routing, rate limiting
Step 9:    Loose coupling, decoupled scaling
Step 10:   High throughput, cache efficiency, horizontal scaling
Step 11:   Reliability, no message loss, fault tolerance
```

## Relevance to OpenCode

### As AGENTS.md Instructions

This repo is a reference for agentic coding tools to understand microservices architecture evolution. Use in `instructions` array:

```json
{
  "instructions": [
    {
      "source": "microservices-patterns",
      "path": "https://github.com/mehmetozkaya/Design-Microservices-Architecture-with-Patterns-Principles",
      "description": "11-step microservices evolution reference — patterns, principles, architecture diagrams"
    }
  ]
}
```

### Key Reference Points for Agentic Coding

| Use Case | Relevant Step(s) |
|----------|-----------------|
| Start a new project → choose architecture | Steps 1-6 (monolith → microservices decision tree) |
| Add database to monolith | Step 2 (PostgreSQL via Aspire) |
| Split monolith into modules | Step 4 (DDD modules, Vertical Slices) |
| Add caching | Steps 5, 10 (Redis → HybridCache) |
| Split modules into microservices | Step 6 (Database per Service, polyglot persistence) |
| Add API Gateway | Step 8 (YARP, rate limiting) |
| Switch from sync to async | Step 9 (RabbitMQ, MassTransit, events) |
| Scale services horizontally | Step 10 (multi-replica, caching) |
| Ensure reliable messaging | Step 11 (Transactional Outbox) |

### Architecture Decision Flow

```
Q: Single process is enough?               → Step 1  (Monolith)
Q: Need persistence?                        → Step 2  (Add DB)
Q: Need separate UI/API teams?              → Step 3  (Separate API)
Q: Codebase too large, need modularity?     → Step 4  (Modular Monolith)
Q: Need faster reads?                       → Step 5  (Add Cache)
Q: Need independent deployability?          → Step 6  (Microservices)
Q: Services need to coordinate?             → Step 7  (Sync Calls)
Q: Need centralized routing/rate limiting?  → Step 8  (API Gateway)
Q: Need loose coupling, async scale?        → Step 9  (Event-Driven)
Q: Need high throughput, low latency?       → Step 10 (Hybrid Cache + Replicas)
Q: Need guaranteed message delivery?        → Step 11 (Outbox Pattern)
```

## Repository Structure

```
/
├── 1-eshop-monolith-one-app/           # Blazor Server + EF Core InMemory
├── 2-eshop-monolith-add-db/            # + PostgreSQL via Aspire
├── 3-eshop-monolith-add-ui/            # ApiService + WebApp split
├── 4-eshop-modular-monoliths-first/    # Domain modules (Catalog/Basket/Ordering)
├── 5-eshop-modular-monoliths-add-cache/ # + Redis cache + RequestSender
├── 6-eshop-microservices-first/        # Separate Web API projects
├── 7-eshop-microservices-sync-call/    # + Sync HTTP between services
├── 8-eshop-microservices-yarp-api-gw/  # + YARP API Gateway
├── 9-eshop-microservices-async-rabbitmq_IDEAL/  # + RabbitMQ + MassTransit
├── 10-eshop-microservices-hybrid-cache/         # + HybridCache + Basket DB + Replicas
├── 11-eshop-microservices-outbox/               # + Transactional Outbox
└── README.md
```

Each step is a complete, runnable .NET Aspire solution. The `AppHost/Program.cs` in each step shows the full infrastructure topology (which services depend on which backing services).
