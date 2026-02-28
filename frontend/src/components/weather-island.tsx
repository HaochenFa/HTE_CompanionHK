"use client";

import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import {
  X,
  Sun,
  Cloud,
  CloudRain,
  CloudSnow,
  CloudLightning,
  CloudFog,
  CloudSun,
  Thermometer,
} from "lucide-react";
import { WeatherDetailsPanel } from "@/components/weather-details-panel";
import { useWeather } from "@/components/weather-provider";
import { springBouncy } from "@/lib/motion-config";

const CONDITION_CONFIG: Record<
  string,
  { icon: typeof Sun; label: string; gradient: string }
> = {
  clear: {
    icon: Sun,
    label: "Clear",
    gradient: "from-amber-400/20 to-orange-300/10",
  },
  rain: {
    icon: CloudRain,
    label: "Rain",
    gradient: "from-blue-400/20 to-slate-400/10",
  },
  drizzle: {
    icon: CloudRain,
    label: "Drizzle",
    gradient: "from-blue-300/20 to-slate-300/10",
  },
  thunderstorm: {
    icon: CloudLightning,
    label: "Storm",
    gradient: "from-purple-400/20 to-slate-500/10",
  },
  cloudy: {
    icon: Cloud,
    label: "Cloudy",
    gradient: "from-stone-300/20 to-amber-200/10",
  },
  partly_cloudy: {
    icon: CloudSun,
    label: "Partly Cloudy",
    gradient: "from-amber-300/15 to-slate-300/10",
  },
  fog: {
    icon: CloudFog,
    label: "Foggy",
    gradient: "from-stone-300/20 to-zinc-200/10",
  },
  snow: {
    icon: CloudSnow,
    label: "Snow",
    gradient: "from-blue-200/20 to-white/10",
  },
};

export function WeatherIsland() {
  const weather = useWeather();
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    if (!isOpen) return;

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") setIsOpen(false);
    };
    window.addEventListener("keydown", onKeyDown);
    return () => {
      document.body.style.overflow = previousOverflow;
      window.removeEventListener("keydown", onKeyDown);
    };
  }, [isOpen]);

  if (weather.condition === "unknown") return null;

  const config = CONDITION_CONFIG[weather.condition] ?? CONDITION_CONFIG.clear;
  const Icon = config.icon;
  const temp =
    weather.temperatureC != null ? `${Math.round(weather.temperatureC)}°` : "--°";

  return (
    <>
      <motion.button
        initial={{ opacity: 0, y: -20, scale: 0.8 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        transition={springBouncy}
        onClick={() => setIsOpen(true)}
        className={`
          group relative flex items-center gap-2 rounded-full
          bg-gradient-to-r ${config.gradient}
          px-3.5 py-1.5 glass glass-border
          cursor-pointer transition-shadow duration-300
          hover:shadow-(--shadow-warm-md)
        `}
        aria-label="Open weather details"
      >
        <motion.div
          animate={{ rotate: weather.condition === "clear" ? [0, 10, -10, 0] : 0 }}
          transition={{ repeat: Infinity, duration: 4, ease: "easeInOut" }}
        >
          <Icon className="size-4 text-foreground/70" />
        </motion.div>

        <span className="text-sm font-semibold text-foreground/90 tabular-nums">
          {temp}
        </span>

        <Thermometer className="size-3 text-muted-foreground/50 opacity-0 transition-opacity group-hover:opacity-100" />
      </motion.button>

      <AnimatePresence>
        {isOpen && (
          <>
            <motion.button
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 z-40 bg-black/25 backdrop-blur-sm"
              onClick={() => setIsOpen(false)}
              aria-label="Close weather dialog backdrop"
            />
            <motion.div
              initial={{ opacity: 0, y: 20, scale: 0.98 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 8, scale: 0.98 }}
              transition={springBouncy}
              className="fixed inset-x-4 top-16 z-50 mx-auto w-full max-w-xl rounded-3xl border border-border/60 bg-background/95 p-4 shadow-(--shadow-warm-lg) glass"
              role="dialog"
              aria-modal="true"
              aria-label="Weather details"
              onClick={(event) => event.stopPropagation()}
            >
              <div className="mb-3 flex items-center justify-between border-b border-border/50 pb-3">
                <p className="text-sm font-semibold text-foreground">Current Weather</p>
                <button
                  type="button"
                  onClick={() => setIsOpen(false)}
                  className="rounded-full p-1 text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
                  aria-label="Close weather details"
                >
                  <X className="size-4" />
                </button>
              </div>
              <WeatherDetailsPanel />
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  );
}
