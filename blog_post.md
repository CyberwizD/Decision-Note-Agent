---
title: 'I Built an AI Agent to End Team Arguments (Mostly) - My HNG Stage 3 Journey'
published: false
description: 'How I survived the HNG Internship Stage 3 task by building a Decision Note Agent with Python, FastAPI, and the Telex.im A2A protocol.'
tags: ['python', 'fastapi', 'ai', 'hnginternship']
---

## The Problem: Team Chats are Where Decisions Go to Die

You know the drill. You're in a team chat. Ideas are flying. Someone makes a great point. Everyone agrees. High-fives all around.

A week later: "Wait, what did we decide about the database again?"

*Crickets.*

The decision is buried under 300 memes, 50 "lols", and a heated debate about whether pineapple belongs on pizza (it doesn't, fight me). Team discussions are great, but they can be black holes for important decisions.

As part of the HNG Internship, my Stage 3 task was to tackle a problem like this. The challenge? Build an AI agent that integrates with a chat platform, Telex.im, to make sense of the chaos.

So, I built the **Decision Note Agent**.

`[Insert Image Here: A screenshot of the agent in action in a chat]`

## What's This Magical Agent You Speak Of?

The Decision Note Agent is a smart assistant that lives in your team chat. Its job is to listen for specific commands, capture decisions, and log them in a structured, searchable way.

No more scrolling endlessly. No more "I thought we agreed on...". Just clear, recorded decisions.

Here's the command list:

*   `/decision propose "Let's use FastAPI for the new service"`: Propose an idea for the team to vote on.
*   `/decision approve [id]`: Approve a proposal.
*   `/decision reject [id]`: Reject a proposal.
*   `/decision add "We will use PostgreSQL"`: Log a decision that's already been made.
*   `/decision list`: See all the decisions.
*   `/decision search "database"`: Find a specific decision.

Simple, right? The goal was to make it as frictionless as possible.

## The Tech Stack: Python, FastAPI, and a Dash of AI

I chose a stack I'm comfortable with but that's also powerful and modern:

*   **Python**: Because it's the undisputed king of AI and backend development.
*   **FastAPI**: It's a modern, fast (hence the name) web framework for building APIs. Its asynchronous nature is perfect for handling real-time chat interactions.
*   **Gemini AI**: To add a little "smart" to the agent, validating decisions and providing summaries.
*   **Telex.im A2A Protocol**: This was the trickiest part. It's the "Agent-to-Agent" protocol that allows my agent to talk to the Telex chat platform.

`[Insert Image Here: A code snippet you're proud of, maybe from the workflow_handlers.py]`

## The Journey: Integrating with Telex.im (and Fighting Bugs)

The core of the task was getting my FastAPI application to communicate with Telex.im. This happens through a "well-known" endpoint (`/.well-known/agent.json`) where my agent advertises its skills, and an A2A endpoint where it receives messages.

Think of it like a job interview. The `agent.json` file is the resume, listing all the cool things my agent can do (`add`, `propose`, `list`, etc.). The A2A endpoint is the interview itself, where the agent has to actually perform those tasks.

The message format is JSON-RPC, which is a standard for remote procedure calls. It's basically a structured JSON object that says, "Hey agent, a user sent this message. Do something with it."

### The Bug Hunt

It wasn't all smooth sailing. My initial build was, to put it mildly, a bit buggy. The logs were filled with "Unknown command" and "Error while streaming". It was like the agent was having a really bad day at the office.

After a lot of coffee and `print()` statements, I found the culprits:

1.  **The Clueless Agent:** My `agent.json` file was missing half the commands! I was telling Telex my agent could only `add` and `list`, so when a user tried to `propose` or `reject`, Telex was (rightfully) confused. **Fix:** I updated the `well_known.py` file to include all the commands.

2.  **The Mismatched Payloads:** My main message handler was correctly parsing the command from a complex JSON payload, but the individual command functions were looking for it in the wrong place. It was a classic case of the left hand not knowing what the right hand was doing. **Fix:** I refactored `workflow_handlers.py` to pass the correct message text down to every function.

`[Insert Image Here: The "Error while streaming" log message, for dramatic effect]`

## How It All Came Together

After fixing the bugs and updating my README to reflect the *actual* project structure (whoops), it finally worked. The agent was listening, responding, and logging decisions like a champ.

This HNG task was a rollercoaster. It pushed me to not just write code, but to think about architecture, protocols, and the real-world usability of a tool. It's one thing to build an API; it's another to make it a helpful participant in a team conversation.

If you want to check out the code, you can find the full project on my GitHub.

`[Link to your GitHub repository]`

Thanks for reading! Now, go make some (well-documented) decisions.
