"use client";

import { motion } from "framer-motion";
import { ArrowLeft } from "lucide-react";
import { useRouter } from "next/navigation";
import { WeatherBackground } from "@/components/weather-background";
import { WeatherDetailsPanel } from "@/components/weather-details-panel";
import { Button } from "@/components/ui/button";
import { springGentle } from "@/lib/motion-config";

export default function WeatherPage() {
  const router = useRouter();

  return (
    <div className="relative min-h-dvh overflow-hidden bg-background">
      <WeatherBackground />

      <div className="relative z-10 mx-auto max-w-xl px-4 py-6">
        <motion.div
          initial={{ opacity: 0, x: -12 }}
          animate={{ opacity: 1, x: 0 }}
          transition={springGentle}
        >
          <Button
            variant="ghost"
            size="sm"
            onClick={() => router.back()}
            className="mb-4 gap-1.5 rounded-xl"
          >
            <ArrowLeft className="size-4" />
            Back
          </Button>
        </motion.div>
        <WeatherDetailsPanel />
      </div>
    </div>
  );
}
