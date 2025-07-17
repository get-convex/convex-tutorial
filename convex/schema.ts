import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  canvas: defineTable({
    body: v.string(),
  }),
});
