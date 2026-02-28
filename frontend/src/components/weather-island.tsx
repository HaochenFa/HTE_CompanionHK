"use client";

import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import {
  Sun,
  Cloud,
  CloudRain,
  CloudSnow,
  CloudLightning,
  CloudFog,
  CloudSun,
  Thermometer,
} from "lucide-react";
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
    gradient: "from-slate-300/20 to-gray-200/10",
  },
  partly_cloudy: {
    icon: CloudSun,
    label: "Partly Cloudy",
    gradient: "from-amber-300/15 to-slate-300/10",
  },
  fog: {
    icon: CloudFog,
    label: "Foggy",
    gradient: "from-gray-300/20 to-slate-200/10",
  },
  snow: {
    icon: CloudSnow,
    label: "Snow",
    gradient: "from-blue-200/20 to-white/10",
  },
};

export function WeatherIsland() {
  const weather = useWeather();
  const router = useRouter();

  if (weather.condition === "unknown") return null;

  const config = CONDITION_CONFIG[weather.condition] ?? CONDITION_CONFIG.clear;
  const Icon = config.icon;
  const temp =
    weather.temperatureC != null ? `${Math.round(weather.temperatureC)}°` : "--°";

  return (
    <motion.button
      initial={{ opacity: 0, y: -20, scale: 0.8 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      transition={springBouncy}
      onClick={() => router.push("/weather")}
      className={`
        group relative flex items-center gap-2 rounded-full
        bg-gradient-to-r ${config.gradient}
        px-3.5 py-1.5 glass glass-border
        cursor-pointer transition-shadow duration-300
        hover:shadow-(--shadow-warm-md)
      `}
      aria-label="View weather details"
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
  );
}
