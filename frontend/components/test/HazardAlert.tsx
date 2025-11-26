"use client";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import type { Hazard } from "@/lib/types";
import { AlertTriangle, Clock } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useEffect, useState } from "react";

interface HazardAlertProps {
  hazards: Hazard[];
}

interface PersistentHazard extends Hazard {
  lastSeen: number;
  uniqueKey: string;
}

export function HazardAlert({ hazards }: HazardAlertProps) {
  const [persistentHazards, setPersistentHazards] = useState<
    PersistentHazard[]
  >([]);

  // Update persistent hazards when new hazards arrive
  useEffect(() => {
    if (hazards.length === 0) return;

    const now = Date.now();
    setPersistentHazards((prev) => {
      const next = [...prev];

      hazards.forEach((newHazard) => {
        // Create a unique key for the hazard instance
        const key = `${newHazard.object_id}-${newHazard.class_name}`;
        const existingIndex = next.findIndex((h) => h.uniqueKey === key);

        if (existingIndex >= 0) {
          // Update existing hazard's last seen time
          next[existingIndex] = { ...newHazard, lastSeen: now, uniqueKey: key };
        } else {
          // Add new hazard
          next.push({ ...newHazard, lastSeen: now, uniqueKey: key });
        }
      });

      return next;
    });
  }, [hazards]);

  // Clean up old hazards every second
  useEffect(() => {
    const interval = setInterval(() => {
      const now = Date.now();
      setPersistentHazards(
        (prev) => prev.filter((h) => now - h.lastSeen < 1000 * 10), // Keep for 10 seconds
      );
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  if (persistentHazards.length === 0) return null;

  // Sort hazards: High priority first, then by most recently seen
  const sortedHazards = [...persistentHazards].sort((a, b) => {
    if (a.priority === "high" && b.priority !== "high") return -1;
    if (a.priority !== "high" && b.priority === "high") return 1;
    return b.lastSeen - a.lastSeen;
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <AlertTriangle className="h-5 w-5 text-destructive" />
          Active Hazards
        </h3>
        <Badge variant="outline" className="text-xs">
          Auto-clear in 10s
        </Badge>
      </div>

      <AnimatePresence mode="popLayout">
        {sortedHazards.map((hazard) => (
          <motion.div
            key={hazard.uniqueKey}
            layout
            initial={{ opacity: 0, y: -20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9, transition: { duration: 0.2 } }}
          >
            <Alert
              variant={hazard.priority === "high" ? "destructive" : "default"}
              className={`${
                hazard.priority === "medium"
                  ? "border-yellow-500 bg-yellow-500/10 dark:bg-yellow-500/20"
                  : ""
              } shadow-sm`}
            >
              <AlertTriangle
                className={`h-4 w-4 ${
                  hazard.priority === "medium"
                    ? "text-yellow-600 dark:text-yellow-500"
                    : ""
                }`}
              />
              <AlertTitle
                className={`flex items-center gap-2 ${
                  hazard.priority === "medium"
                    ? "text-yellow-700 dark:text-yellow-400"
                    : ""
                }`}
              >
                {hazard.priority === "high"
                  ? "High Priority Hazard"
                  : "Hazard Warning"}
                <span className="text-xs font-normal opacity-70 ml-auto flex items-center gap-1">
                  <Clock className="h-3 w-3" />
                  {Math.round((Date.now() - hazard.lastSeen) / 1000)}s ago
                </span>
              </AlertTitle>
              <AlertDescription className="mt-2 flex items-center gap-2">
                <Badge
                  variant={
                    hazard.priority === "high" ? "destructive" : "outline"
                  }
                  className={
                    hazard.priority === "medium"
                      ? "border-yellow-500 text-yellow-700 dark:text-yellow-400"
                      : ""
                  }
                >
                  {hazard.class_name}
                </Badge>
                <span
                  className={
                    hazard.priority === "medium"
                      ? "text-yellow-700 dark:text-yellow-400"
                      : ""
                  }
                >
                  {hazard.reason}
                </span>
              </AlertDescription>
            </Alert>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
