"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Heart, MapPin, BookOpen, ArrowRight, Shield, Sparkles } from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { WeatherBackground } from "@/components/weather-background";
import { Button } from "@/components/ui/button";
import { springGentle, springBouncy } from "@/lib/motion-config";

const ROLES = [
  {
    label: "Companion",
    icon: Heart,
    color: "var(--role-companion)",
    description: "Warm emotional support and daily companionship.",
  },
  {
    label: "Local Guide",
    icon: MapPin,
    color: "var(--role-local-guide)",
    description: "Discover Hong Kong places, routes, and local tips.",
  },
  {
    label: "Study Guide",
    icon: BookOpen,
    color: "var(--role-study-guide)",
    description: "Plan study sessions and break down topics.",
  },
];

const TRUST_CUES = [
  "Powered by MiniMax AI",
  "Voice by ElevenLabs & Cantonese.ai",
  "Hosted on AWS",
  "Real-time search by Exa",
];

export default function WelcomePage() {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && user) {
      router.replace("/");
    }
  }, [isLoading, user, router]);

  return (
    <div className="relative min-h-dvh overflow-hidden bg-background">
      <WeatherBackground />

      <div className="relative z-10 mx-auto flex min-h-dvh max-w-lg flex-col items-center justify-center px-6 py-12">
        {/* Logo + Title */}
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={springBouncy}
          className="mb-2 flex size-20 items-center justify-center rounded-3xl bg-primary/10"
        >
          <Heart className="size-10 text-primary" fill="currentColor" />
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1, ...springGentle }}
          className="mb-1 text-center text-3xl font-bold font-heading text-foreground"
        >
          港伴<span className="text-primary">AI</span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.18, ...springGentle }}
          className="mb-8 text-center text-base text-muted-foreground leading-relaxed"
        >
          Your warm AI companion for Hong Kong —<br />
          supportive, local, and always here for you.
        </motion.p>

        {/* Role Preview Cards */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.26, ...springGentle }}
          className="mb-8 flex w-full flex-col gap-3"
        >
          {ROLES.map((role, i) => (
            <motion.div
              key={role.label}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 + i * 0.08, ...springGentle }}
              className="flex items-center gap-3 rounded-2xl border border-border/50 bg-card/70 px-4 py-3 glass glass-border"
            >
              <div
                className="flex size-10 shrink-0 items-center justify-center rounded-xl"
                style={{ backgroundColor: `color-mix(in srgb, ${role.color} 15%, transparent)` }}
              >
                <role.icon className="size-5" style={{ color: role.color }} />
              </div>
              <div className="min-w-0">
                <p className="text-sm font-semibold text-foreground">{role.label}</p>
                <p className="text-xs text-muted-foreground">{role.description}</p>
              </div>
            </motion.div>
          ))}
        </motion.div>

        {/* Safety Cue */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.55, ...springGentle }}
          className="mb-6 flex items-center gap-2 rounded-full border border-border/40 bg-card/60 px-4 py-2 text-xs text-muted-foreground glass glass-border"
        >
          <Shield className="size-3.5 text-primary" />
          <span>Built with care for your wellbeing and privacy</span>
        </motion.div>

        {/* CTA */}
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.62, ...springGentle }}
          className="w-full"
        >
          <Button
            size="lg"
            className="w-full rounded-xl text-base"
            onClick={() => router.push("/login")}
          >
            Get Started
            <ArrowRight className="ml-2 size-4" />
          </Button>
        </motion.div>

        {/* Sponsor Trust Strip */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.75 }}
          className="mt-8 flex flex-wrap items-center justify-center gap-x-3 gap-y-1"
        >
          {TRUST_CUES.map((cue) => (
            <span key={cue} className="text-[0.65rem] text-muted-foreground/40">
              {cue}
            </span>
          ))}
        </motion.div>

        {/* Footer */}
        <motion.footer
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.85 }}
          className="mt-6 flex items-center gap-1.5 text-xs text-muted-foreground/30"
        >
          <Sparkles className="size-3" />
          <span>Built with care for Hong Kong</span>
        </motion.footer>
      </div>
    </div>
  );
}
