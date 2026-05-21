#!/usr/bin/env node
// .claude/hooks/PostToolUse/skip_summary_after_commit/main.js

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

import { SIGNAL_FILE, getLogger } from "../utils.js";

const logger = getLogger("skip_summary_after_commit_hook");

function main() {
  logger.log("Hook started");
  const raw = fs.readFileSync("/dev/stdin", "utf-8");
  const data = JSON.parse(raw);
  logger.log("Parsed payload", {
    session_id: data.session_id,
    tool_input_present: !!data.tool_input,
    command: data.tool_input?.command ?? null,
  });

  const command = data.tool_input?.command ?? "";
  if (!command.includes("git commit")) {
    logger.log("Command does not include 'git commit', skipping", { command });
    return;
  }
  else {
    logger.log("Git commit detected in command, creating signal file", { command });
    fs.writeFileSync(SIGNAL_FILE, new Date().toISOString());
  }
  
  logger.log("Hook finished");
}

main();