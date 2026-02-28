"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import {
  Heart,
  MapPin,
  BookOpen,
  ArrowRight,
  LogOut,
  Sparkles,
} from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { WeatherBackground } from "@/components/weather-background";
import { WeatherIsland } from "@/components/weather-island";
import { Button } from "@/components/ui/button";
import { springGentle, springBouncy } from "@/lib/motion-config";
import type { Role } from "@/features/chat/types";
import { roleToSlug } from "@/features/chat/role-routing";

const ROLES: {
  id: Role;
  label: string;
  description: string;
  icon: typeof Heart;
  color: string;
  gradient: string;
  tagline: string;
}[] = [
  {
    id: "companion",
    label: "Companion",
    description: "Talk about your feelings, get encouragement, and find emotional support.",
    icon: Heart,
    color: "var(--role-companion)",
    gradient: "from-rose-400/20 via-orange-300/10 to-transparent",
    tagline: "Your safe space to talk",
  },
  {
    id: "local_guide",
    label: "Local Guide",
    description: "Discover places, food, events, and get around Hong Kong like a local.",
    icon: MapPin,
    color: "var(--role-local-guide)",
    gradient: "from-emerald-400/20 via-teal-300/10 to-transparent",
    tagline: "Explore Hong Kong with AI",
  },
  {
    id: "study_guide",
    label: "Study Guide",
    description: "Break down topics, plan your study sessions, and ace your exams.",
    icon: BookOpen,
    color: "var(--role-study-guide)",
    gradient: "from-indigo-400/20 via-blue-300/10 to-transparent",
    tagline: "Learn smarter, not harder",
  },
];

export default function HomePage() {
  const { user, isLoading, logout } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !user) {
      router.push("/login");
    }
  }, [isLoading, user, router]);

  if (isLoading || !user) {
    return (
      <div className="flex min-h-dvh items-center justify-center bg-background">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
          className="size-8 rounded-full border-2 border-primary border-t-transparent"
        />
      </div>
    );
  }

  return (
    <div className="relative min-h-dvh overflow-hidden bg-background">
      <WeatherBackground />

      <div className="relative z-10 mx-auto flex min-h-dvh max-w-lg flex-col px-4 py-6">
        {/* Header */}
        <motion.header
          initial={{ opacity: 0, y: -12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={springGentle}
          className="mb-8 flex items-center justify-between"
        >
          <div className="flex items-center gap-3">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={springBouncy}
              className="flex size-10 items-center justify-center rounded-xl bg-primary/10"
            >
              <Heart className="size-5 text-primary" fill="currentColor" />
            </motion.div>
            <div>
              <h1 className="text-lg font-bold font-heading text-foreground">
                港伴<span className="text-primary">AI</span>
              </h1>
              <p className="text-xs text-muted-foreground">
                Hi, {user.displayName}!
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <WeatherIsland />
            <Button
              variant="ghost"
              size="icon-sm"
              onClick={logout}
              className="rounded-lg text-muted-foreground"
              aria-label="Log out"
            >
              <LogOut className="size-4" />
            </Button>
          </div>
        </motion.header>

        {/* Welcome Message */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1, ...springGentle }}
          className="mb-8"
        >
          <h2 className="mb-2 text-2xl font-bold font-heading text-foreground">
            What would you like{" "}
            <span className="text-primary">today</span>?
          </h2>
          <p className="text-sm text-muted-foreground leading-relaxed">
            Choose a role and start chatting. Each space has its own conversation history.
          </p>
        </motion.div>

        {/* Role Cards */}
        <div className="flex flex-1 flex-col gap-4">
          {ROLES.map((role, i) => (
            <motion.button
              key={role.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.15 + i * 0.08, ...springGentle }}
              whileHover={{ scale: 1.02, y: -2 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => router.push(`/chat/${roleToSlug(role.id)}`)}
              className={`
                group relative overflow-hidden rounded-2xl border border-border/50
                bg-card/70 p-5 text-left shadow-(--shadow-warm-sm)
                glass glass-border cursor-pointer
                transition-shadow duration-300 hover:shadow-(--shadow-warm-md)
              `}
            >
              {/* Gradient overlay */}
              <div
                className={`absolute inset-0 bg-gradient-to-br ${role.gradient} opacity-0 transition-opacity duration-300 group-hover:opacity-100`}
              />

              <div className="relative z-10 flex items-start gap-4">
                <motion.div
                  whileHover={{ rotate: [0, -10, 10, 0] }}
                  transition={{ duration: 0.4 }}
                  className="flex size-12 shrink-0 items-center justify-center rounded-xl"
                  style={{ backgroundColor: `color-mix(in srgb, ${role.color} 15%, transparent)` }}
                >
                  <role.icon className="size-6" style={{ color: role.color }} />
                </motion.div>

                <div className="min-w-0 flex-1">
                  <div className="mb-0.5 flex items-center gap-2">
                    <h3 className="text-base font-bold font-heading text-foreground">
                      {role.label}
                    </h3>
                    <span
                      className="rounded-full px-2 py-0.5 text-[0.6rem] font-semibold uppercase tracking-wide"
                      style={{
                        backgroundColor: `color-mix(in srgb, ${role.color} 12%, transparent)`,
                        color: role.color,
                      }}
                    >
                      {role.tagline}
                    </span>
                  </div>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    {role.description}
                  </p>
                </div>

                <ArrowRight
                  className="mt-1 size-5 shrink-0 text-muted-foreground/40 transition-all duration-200 group-hover:translate-x-1 group-hover:text-foreground/60"
                />
              </div>
            </motion.button>
          ))}
        </div>

        {/* Footer */}
        <motion.footer
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="mt-8 flex items-center justify-center gap-1.5 pb-4 text-xs text-muted-foreground/40"
        >
          <Sparkles className="size-3" />
          <span>Built with care for Hong Kong</span>
        </motion.footer>
      </div>
    </div>
  );
}
