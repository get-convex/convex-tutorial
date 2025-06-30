import { internalAction, mutation, query } from "./_generated/server";
import { v } from "convex/values";
import { api, internal } from "./_generated/api";

export const sendMessage = mutation({
  args: {
    user: v.string(),
    body: v.string(),
  },
  handler: async (ctx, args) => {
    console.log("This TypeScript function is running on the server.");
    await ctx.db.insert("messages", {
      user: args.user,
      body: args.body,
    });

    if (args.body.startsWith("/wiki")) {
      const topic = args.body.slice(args.body.indexOf(" ") + 1);
      await ctx.scheduler.runAfter(0, internal.chat.getWikipediaSummary, {
        topic,
      });
    }
  },
});

export const getMessages = query({
  args: { nameFilter: v.optional(v.string()) },
  handler: async (ctx, args) => {
    let query = ctx.db.query("messages");

    // Only apply filter if nameFilter has a value
    if (args.nameFilter)
      query = query.filter((q) => q.eq(q.field("user"), args.nameFilter));

    const messages = await query.order("desc").take(50);

    // Reverse the list so that it's in a chronological order.
    return messages.reverse();
  },
});

export const getWikipediaSummary = internalAction({
  args: { topic: v.string() },
  handler: async (ctx, args) => {
    const response = await fetch(
      "https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro&explaintext&redirects=1&titles=" +
        args.topic
    );

    const summary = getSummaryFromJSON(await response.json());

    await ctx.scheduler.runAfter(0, api.chat.sendMessage, {
      user: "Wikipedia",
      body: summary,
    });
  },
});

function getSummaryFromJSON(data: any) {
  const firstPageId = Object.keys(data.query.pages)[0];
  return data.query.pages[firstPageId].extract;
}
