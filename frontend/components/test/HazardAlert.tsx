"use client";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import type { Hazard } from "@/lib/types";
import { AlertTriangle, Clock, ShieldAlert } from "lucide-react";
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
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold flex items-center gap-2 text-foreground">
          <ShieldAlert className="h-4 w-4" />
          Active Hazards
        </h3>
      </div>

      <AnimatePresence mode="popLayout">
        {sortedHazards.map((hazard) => (
          <motion.div
            key={hazard.uniqueKey}
            layout
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, scale: 0.95, transition: { duration: 0.2 } }}
          >
            <Alert
              className={`${
                hazard.priority === "high"
                  ? "border-destructive/50 bg-destructive/5 text-destructive"
                  : "border-yellow-500/50 bg-yellow-500/5 text-yellow-600 dark:text-yellow-500"
              } shadow-sm`}
            >
              <AlertTriangle className="h-4 w-4" />
              <div className="flex-1">
                <AlertTitle className="flex items-center gap-2 mb-1">
                  <span className="font-semibold text-sm tracking-tight">
                    {hazard.priority === "high" ? "CRITICAL ALERT" : "WARNING"}
                  </span>
                  <span className="text-[10px] font-normal opacity-70 ml-auto font-mono">
                    {Math.round((Date.now() - hazard.lastSeen) / 1000)}s
                  </span>
                </AlertTitle>
                <AlertDescription className="flex items-center justify-between gap-2">
                  <span className="text-xs opacity-90">{hazard.reason}</span>
                  <Badge
                    variant="outline"
                    className={`text-[10px] uppercase tracking-wider h-5 ${
                      hazard.priority === "high"
                        ? "border-destructive text-destructive"
                        : "border-yellow-500 text-yellow-600 dark:text-yellow-500"
                    }`}
                  >
                    {hazard.class_name}
                  </Badge>
                </AlertDescription>
              </div>
            </Alert>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
