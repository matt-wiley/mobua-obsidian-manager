#!/usr/bin/env node
// .claude/hooks/Stop/summarize_turn/main.js

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

import { SIGNAL_FILE, LOG_PATH, HOOKS_ROOT, getLogger } from "../utils.js";

const logger = getLogger("summarize_turn_hook");

function getLastUserMessage(transcriptPath) {
  if (!transcriptPath || !fs.existsSync(transcriptPath)) {
    logger.log("Transcript file not found", { transcriptPath });
    return "";
  }

  const raw = fs.readFileSync(transcriptPath, "utf-8");
  const lines = raw.trim().split("\n").filter(Boolean);

  for (const line of [...lines].reverse()) {
    try {
      const entry = JSON.parse(line);
      if (entry.type === "user" && entry.message?.role === "user") {
        const content = entry.message.content;
        if (typeof content === "string") return content;
        if (Array.isArray(content)) {
          return content.find(c => c.type === "text")?.text ?? "";
        }
      }
    } catch {
      continue;
    }
  }
  return "";
}

async function main() {
  logger.log("Hook started");

  if (fs.existsSync(SIGNAL_FILE)) {
    logger.log("Signal file found, skipping summarization");
    fs.unlinkSync(SIGNAL_FILE);
    process.exit(0);
  }

  const raw = fs.readFileSync("/dev/stdin", "utf-8");
  const data = JSON.parse(raw);
  logger.log("Parsed payload", {
    session_id: data.session_id,
    stop_hook_active: data.stop_hook_active,
    has_transcript_path: !!data.transcript_path,
    has_last_assistant_message: !!data.last_assistant_message,
  });

  if (data.stop_hook_active) {
    log("stop_hook_active is true, exiting early");
    process.exit(0);
  }

  // Use last_assistant_message directly from payload
  const lastAssistant = data.last_assistant_message ?? "";

  // Read last user message from the transcript .jsonl file
  const lastUser = getLastUserMessage(data.transcript_path);

  logger.log("Extracted messages", {
    lastUser: lastUser.slice(0, 100),
    lastAssistant: lastAssistant.slice(0, 100),
  });

  if (!lastUser && !lastAssistant) {
    logger.log("No content to summarize, exiting");
    process.exit(0);
  }

  const previousSummaries = fs.existsSync(LOG_PATH)
    ? fs.readFileSync(LOG_PATH, "utf-8").trim().split("\n").slice(-10).join("\n")
    : "";

  logger.log("Calling Claude API");
  const response = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": process.env.HOOKS_API_KEY,
      "anthropic-version": "2023-06-01",
    },
    body: JSON.stringify({
      model: "claude-haiku-4-5-20251001",
      max_tokens: 100,
      messages: [
        {
          role: "user",
          content: `Goal: Summarize this Claude Code interaction in ONE sentence. Be specific and concrete.

**Important**: Seek first to understand the interaction, then summarize.

${previousSummaries ? `For additional context, here are the most recent summaries you've written:\n${previousSummaries}\n\n` : ""}

**Interaction to summarize:**

User asked: ${lastUser.slice(0, 500)}
Claude did: ${lastAssistant.slice(0, 1000)}

**Output format**:
- Follow the format and style of the previous summaries (if any).
- Write ONE concise sentence that captures the essence or outcome of the interaction.

**Important**: Output only the one-line summary, nothing else.`,
        },
      ],
    }),
  });

  logger.log("API response received", { status: response.status });

  const result = await response.json();
  const summary = result.content[0].text.trim();
  logger.log("Summary extracted", { summary });

  const logPath = path.join(HOOKS_ROOT, "..", "interaction_log.txt");
  const timestamp = new Date().toISOString().slice(0, 16).replace("T", " ");
  fs.appendFileSync(logPath, `${timestamp} | ${summary}\n`);
  logger.log("Interaction log written", { logPath });

  process.stderr.write(`📝 ${summary}\n`);
  logger.log("Hook completed successfully");
}

main().catch((err) => {
  logger.log("Unhandled error", { message: err.message, stack: err.stack });
  process.stderr.write(`Hook error: ${err.message}\n`);
  process.exit(0);
});