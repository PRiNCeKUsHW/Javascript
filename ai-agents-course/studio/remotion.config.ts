/**
 * Note: When using the Node.JS APIs, the config file
 * doesn't apply. Instead, pass options directly to the APIs.
 *
 * All configuration options: https://remotion.dev/docs/config
 */

import { Config } from "@remotion/cli/config";

Config.setRspack(true);
Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);
Config.setDefaultPremountInSeconds(2);
// Use a pre-installed headless Chromium when REMOTION_BROWSER (or the cloud default) exists;
// otherwise Remotion downloads its own browser on first render.
import fs from "node:fs";
const browser = process.env.REMOTION_BROWSER ?? "/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell";
if (fs.existsSync(browser)) Config.setBrowserExecutable(browser);
Config.setConcurrency(Number(process.env.REMOTION_CONCURRENCY ?? 4));
