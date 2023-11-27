import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  messages: defineTable({
    body: v.string(),
    author: v.string(),
  }).index("by_author_body", ["author", "body"]),
  users: defineTable({
    name: v.string(),
  }).index("by_name", ["name"]),
});
