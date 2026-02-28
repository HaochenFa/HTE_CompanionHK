"use client";

import { motion } from "framer-motion";
import {
  Sun,
  Cloud,
  CloudRain,
  CloudSnow,
  CloudLightning,
  CloudFog,
  CloudSun,
  Droplets,
  Wind,
  Thermometer,
  Eye as EyeIcon,
} from "lucide-react";
import { useWeather } from "@/components/weather-provider";
import { springBouncy, springGentle } from "@/lib/motion-config";

const CONDITION_DETAILS: Record<
  string,
  { icon: typeof Sun; label: string; advice: string; emoji: string }
> = {
  clear: {
    icon: Sun,
    label: "Clear Sky",
    advice: "Perfect day to explore Hong Kong. A light layer and water are enough.",
    emoji: "sunny",
  },
  rain: {
    icon: CloudRain,
    label: "Rainy",
    advice: "Bring an umbrella. Indoor plans and cozy cafe stops are a great fit.",
    emoji: "rainy",
  },
  drizzle: {
    icon: CloudRain,
    label: "Light Drizzle",
    advice: "A hood or compact umbrella should cover you for short walks.",
    emoji: "drizzle",
  },
  thunderstorm: {
    icon: CloudLightning,
    label: "Thunderstorm",
    advice: "Best to stay indoors until conditions calm down.",
    emoji: "storm",
  },
  cloudy: {
    icon: Cloud,
    label: "Cloudy",
    advice: "Comfortable for longer outdoor plans without harsh sunlight.",
    emoji: "cloudy",
  },
  partly_cloudy: {
    icon: CloudSun,
    label: "Partly Cloudy",
    advice: "Pleasant weather for both indoor and outdoor activities.",
    emoji: "partly_cloudy",
  },
  fog: {
    icon: CloudFog,
    label: "Foggy",
    advice: "Visibility can be limited. Plan extra travel time.",
    emoji: "foggy",
  },
  snow: {
    icon: CloudSnow,
    label: "Snowy",
    advice: "Rare in Hong Kong. Dress warm and watch for slippery paths.",
    emoji: "snow",
  },
  unknown: {
    icon: Cloud,
    label: "Loading...",
    advice: "Fetching current weather data for Hong Kong.",
    emoji: "weather",
  },
};

const DETAIL_ROWS = [
  { icon: Droplets, label: "Humidity", value: "78%" },
  { icon: Wind, label: "Wind", value: "12 km/h" },
  { icon: EyeIcon, label: "Visibility", value: "10 km" },
  { icon: Thermometer, label: "Feels Like", value: null },
];

export function WeatherDetailsPanel() {
  const weather = useWeather();
  const config = CONDITION_DETAILS[weather.condition] ?? CONDITION_DETAILS.unknown;
  const Icon = config.icon;
  const temp = weather.temperatureC != null ? `${Math.round(weather.temperatureC)}` : "--";

  const details = DETAIL_ROWS.map((row) => ({
    ...row,
    value:
      row.label === "Feels Like" && weather.temperatureC != null
        ? `${Math.round(weather.temperatureC)}degC`
        : row.value,
  }));

  return (
    <div className="flex flex-col gap-4">
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={springGentle}
        className="rounded-3xl border border-border/60 bg-card/70 p-6 shadow-(--shadow-warm-lg) glass glass-border"
      >
        <div className="mb-6 flex items-center justify-between">
          <div>
            <p className="text-sm text-muted-foreground">Hong Kong</p>
            <p className="text-xs text-muted-foreground/60">
              {new Date().toLocaleDateString("en-HK", {
                weekday: "long",
                month: "long",
                day: "numeric",
              })}
            </p>
          </div>
          <motion.span
            animate={{ scale: [1, 1.12, 1] }}
            transition={{ repeat: Infinity, duration: 3, ease: "easeInOut" }}
            className="rounded-full bg-primary/10 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-primary"
          >
            {config.emoji}
          </motion.span>
        </div>

        <div className="mb-5 flex items-end gap-3">
          <motion.span
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={springBouncy}
            className="text-6xl font-bold font-heading leading-none tabular-nums text-foreground"
          >
            {temp}
          </motion.span>
          <span className="mb-1 text-2xl font-light text-muted-foreground">degC</span>
        </div>

        <div className="mb-3 flex items-center gap-2">
          <Icon className="size-5 text-primary" />
          <span className="text-lg font-semibold text-foreground">{config.label}</span>
        </div>
        <p className="text-sm leading-relaxed text-muted-foreground">{config.advice}</p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.08, ...springGentle }}
        className="grid grid-cols-2 gap-3"
      >
        {details.map((detail, index) => (
          <motion.div
            key={detail.label}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.12 + index * 0.04, ...springGentle }}
            className="flex items-center gap-3 rounded-2xl border border-border/40 bg-card/60 px-4 py-3 glass glass-border"
          >
            <detail.icon className="size-4 text-muted-foreground/70" />
            <div>
              <p className="text-xs text-muted-foreground">{detail.label}</p>
              <p className="text-sm font-semibold text-foreground">{detail.value}</p>
            </div>
          </motion.div>
        ))}
      </motion.div>
    </div>
  );
}
