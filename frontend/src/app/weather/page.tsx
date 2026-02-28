"use client";

import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import {
  ArrowLeft,
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
import { WeatherBackground } from "@/components/weather-background";
import { Button } from "@/components/ui/button";
import { springGentle, springBouncy } from "@/lib/motion-config";

const CONDITION_DETAILS: Record<
  string,
  { icon: typeof Sun; label: string; advice: string; emoji: string }
> = {
  clear: {
    icon: Sun,
    label: "Clear Sky",
    advice: "Perfect day to explore Hong Kong! Don't forget sunscreen.",
    emoji: "☀️",
  },
  rain: {
    icon: CloudRain,
    label: "Rainy",
    advice: "Bring an umbrella. Great day for indoor activities or a cozy cha chaan teng.",
    emoji: "🌧️",
  },
  drizzle: {
    icon: CloudRain,
    label: "Light Drizzle",
    advice: "Light rain — a jacket with a hood should be enough.",
    emoji: "🌦️",
  },
  thunderstorm: {
    icon: CloudLightning,
    label: "Thunderstorm",
    advice: "Stay indoors if possible. Perfect time for studying or a movie.",
    emoji: "⛈️",
  },
  cloudy: {
    icon: Cloud,
    label: "Cloudy",
    advice: "Overcast but comfortable. Good for hiking without harsh sun.",
    emoji: "☁️",
  },
  partly_cloudy: {
    icon: CloudSun,
    label: "Partly Cloudy",
    advice: "Pleasant weather with some clouds. Enjoy the outdoors!",
    emoji: "⛅",
  },
  fog: {
    icon: CloudFog,
    label: "Foggy",
    advice: "Limited visibility. Take care if travelling. The Peak views may be obscured.",
    emoji: "🌫️",
  },
  snow: {
    icon: CloudSnow,
    label: "Snowy",
    advice: "Rare for Hong Kong! Bundle up and enjoy the unusual weather.",
    emoji: "❄️",
  },
  unknown: {
    icon: Cloud,
    label: "Loading...",
    advice: "Fetching current weather data for Hong Kong.",
    emoji: "🌤️",
  },
};

const MOCK_DETAILS = [
  { icon: Droplets, label: "Humidity", value: "78%" },
  { icon: Wind, label: "Wind", value: "12 km/h" },
  { icon: EyeIcon, label: "Visibility", value: "10 km" },
  { icon: Thermometer, label: "Feels Like", value: null },
];

export default function WeatherPage() {
  const weather = useWeather();
  const router = useRouter();

  const config = CONDITION_DETAILS[weather.condition] ?? CONDITION_DETAILS.unknown;
  const Icon = config.icon;
  const temp =
    weather.temperatureC != null ? `${Math.round(weather.temperatureC)}` : "--";

  const details = MOCK_DETAILS.map((d) => ({
    ...d,
    value: d.label === "Feels Like" && weather.temperatureC != null
      ? `${Math.round(weather.temperatureC - 1 + Math.random() * 2)}°C`
      : d.value,
  }));

  return (
    <div className="relative min-h-dvh overflow-hidden bg-background">
      <WeatherBackground />

      <div className="relative z-10 mx-auto max-w-lg px-4 py-6">
        {/* Back Button */}
        <motion.div
          initial={{ opacity: 0, x: -12 }}
          animate={{ opacity: 1, x: 0 }}
          transition={springGentle}
        >
          <Button
            variant="ghost"
            size="sm"
            onClick={() => router.back()}
            className="mb-6 gap-1.5 rounded-xl"
          >
            <ArrowLeft className="size-4" />
            Back
          </Button>
        </motion.div>

        {/* Main Weather Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={springGentle}
          className="rounded-3xl border border-border/60 bg-card/70 p-8 shadow-(--shadow-warm-lg) glass glass-border"
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
              animate={{ scale: [1, 1.15, 1] }}
              transition={{ repeat: Infinity, duration: 3, ease: "easeInOut" }}
              className="text-4xl"
            >
              {config.emoji}
            </motion.span>
          </div>

          {/* Temperature */}
          <div className="mb-6 flex items-end gap-3">
            <motion.span
              initial={{ opacity: 0, scale: 0.5 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={springBouncy}
              className="text-7xl font-bold font-heading text-foreground leading-none tabular-nums"
            >
              {temp}
            </motion.span>
            <span className="mb-2 text-3xl font-light text-muted-foreground">°C</span>
          </div>

          {/* Condition */}
          <div className="mb-4 flex items-center gap-2">
            <Icon className="size-5 text-primary" />
            <span className="text-lg font-semibold text-foreground">{config.label}</span>
          </div>

          <p className="text-sm text-muted-foreground leading-relaxed">{config.advice}</p>
        </motion.div>

        {/* Detail Cards */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1, ...springGentle }}
          className="mt-4 grid grid-cols-2 gap-3"
        >
          {details.map((detail, i) => (
            <motion.div
              key={detail.label}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.15 + i * 0.05, ...springGentle }}
              className="flex items-center gap-3 rounded-2xl border border-border/40 bg-card/60 px-4 py-3 glass glass-border"
            >
              <detail.icon className="size-4 text-muted-foreground/60" />
              <div>
                <p className="text-xs text-muted-foreground">{detail.label}</p>
                <p className="text-sm font-semibold text-foreground">{detail.value}</p>
              </div>
            </motion.div>
          ))}
        </motion.div>

        {/* Tip Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, ...springGentle }}
          className="mt-4 rounded-2xl border border-primary/20 bg-primary/5 px-5 py-4 glass-border"
        >
          <p className="text-xs font-semibold text-primary">Weather Tip</p>
          <p className="mt-1 text-sm text-foreground/80">
            {config.advice}
          </p>
        </motion.div>
      </div>
    </div>
  );
}
