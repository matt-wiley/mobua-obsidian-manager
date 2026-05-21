import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export const HOOKS_ROOT = __dirname;
export const SIGNAL_FILE = path.join(__dirname, "skip_summarize.local");
export const LOG_PATH = path.join(__dirname, "hooks_log.local.txt");

export function log(source, message, data = null) {
  const timestamp = new Date().toISOString();
  const line = data
    ? `${timestamp} | ${source}: ${message}: ${JSON.stringify(data, null, 2)}\n`
    : `${timestamp} | ${source}: ${message}\n`;
  fs.appendFileSync(LOG_PATH, line);
}

export function getLogger(source) {
  return {
    log: (message, data = null) => {
      log(source, message, data);
    }
  };
}