import { v } from "convex/values";
import { query, mutation, app } from "./_generated/server";

export const list = query(async (ctx) => {
  return await ctx.db.query("messages").collect();
});

export const send = mutation({
  args: { body: v.string(), author: v.string() },
  handler: async (ctx, { body, author }) => {
    const message = { body, author };
    await ctx.db.insert("messages", message);
    // @ts-ignore
    await ctx.runMutation(app.logger.log.info, { message: `New message from ${author}: ${body}` });
  },
});
