"use client";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import type { Hazard } from "@/lib/types";
import { AlertTriangle } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface HazardAlertProps {
  hazards: Hazard[];
}

export function HazardAlert({ hazards }: HazardAlertProps) {
  if (hazards.length === 0) return null;

  const highPriorityHazards = hazards.filter((h) => h.priority === "high");
  const mediumPriorityHazards = hazards.filter((h) => h.priority === "medium");

  return (
    <AnimatePresence>
      {(highPriorityHazards.length > 0 || mediumPriorityHazards.length > 0) && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          className="space-y-2"
        >
          {highPriorityHazards.map((hazard, idx) => (
            <Alert key={idx} variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertTitle>High Priority Hazard Detected</AlertTitle>
              <AlertDescription className="flex items-center gap-2">
                <Badge variant="destructive">{hazard.class_name}</Badge>
                <span>{hazard.reason}</span>
              </AlertDescription>
            </Alert>
          ))}

          {mediumPriorityHazards.map((hazard, idx) => (
            <Alert key={idx} className="border-yellow-500 bg-yellow-500/10">
              <AlertTriangle className="h-4 w-4 text-yellow-500" />
              <AlertTitle className="text-yellow-700 dark:text-yellow-400">
                Medium Priority Alert
              </AlertTitle>
              <AlertDescription className="flex items-center gap-2">
                <Badge variant="outline" className="border-yellow-500">
                  {hazard.class_name}
                </Badge>
                <span>{hazard.reason}</span>
              </AlertDescription>
            </Alert>
          ))}
        </motion.div>
      )}
    </AnimatePresence>
  );
}

