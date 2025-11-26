"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

export function AnimatedBackground({ className }: { className?: string }) {
  return (
    <div className={cn("absolute inset-0 overflow-hidden", className)}>
      <motion.div
        className="absolute inset-0 bg-gradient-to-br from-blue-500/20 via-purple-500/20 to-pink-500/20"
        animate={{
          scale: [1, 1.2, 1],
          rotate: [0, 90, 0],
        }}
        transition={{
          duration: 20,
          repeat: Infinity,
          ease: "linear",
        }}
      />
      <motion.div
        className="absolute inset-0 bg-gradient-to-tr from-purple-500/20 via-pink-500/20 to-blue-500/20"
        animate={{
          scale: [1.2, 1, 1.2],
          rotate: [90, 180, 90],
        }}
        transition={{
          duration: 25,
          repeat: Infinity,
          ease: "linear",
        }}
      />
    </div>
  );
}

