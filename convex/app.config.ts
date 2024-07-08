// @ts-ignore
import { defineApp } from "convex/server";

import logger from "../logger/component.config";

const app = defineApp();
const _logger = app.install(logger, { args: {} });

export default app;

