import { useMutation, useQuery } from "convex/react";
import { useEffect, useState, useRef } from "react";
import { api } from "../convex/_generated/api";

export default function App() {
  const canvas = useQuery(api.canvas.getCanvas);
  const setCanvas = useMutation(api.canvas.setCanvas);
  const [text, setText] = useState("");

  const debounceTimeout = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (canvas && canvas.body !== text) {
      setText(canvas.body);
    }
  }, [canvas]);

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newText = e.target.value;
    setText(newText);

    if (debounceTimeout.current) {
      clearTimeout(debounceTimeout.current);
    }

    debounceTimeout.current = setTimeout(() => {
      setCanvas({ body: newText });
    }, 1000);
  };

  return (
    <main className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="w-full max-w-3xl bg-white rounded-3xl shadow-2xl p-8">
      <h1 className="text-4xl font-extrabold mb-6 text-indigo-700 flex items-center gap-2">
        📝 Notepad
      </h1>
      <textarea
        className="w-full h-[70vh] resize-none border-2 border-indigo-200 focus:border-indigo-500 rounded-2xl p-6 text-xl font-mono bg-indigo-50 focus:bg-white outline-none transition-all duration-200 shadow-inner"
        value={text}
        onChange={handleChange}
        placeholder="Start typing your notes here…"
      />
      </div>
    </main>
  );
}
