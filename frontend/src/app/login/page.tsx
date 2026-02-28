"use client";

import { useCallback, useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Heart, LogIn, UserPlus, Eye, EyeOff, Sparkles } from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { WeatherBackground } from "@/components/weather-background";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { spring, springBouncy, springGentle } from "@/lib/motion-config";

type Mode = "login" | "signup";

export default function LoginPage() {
  const { login, signup } = useAuth();
  const router = useRouter();
  const [mode, setMode] = useState<Mode>("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = useCallback(
    async (e: FormEvent) => {
      e.preventDefault();
      setError(null);
      setIsSubmitting(true);

      try {
        if (mode === "login") {
          const ok = await login(username, password);
          if (!ok) {
            setError("Invalid username or password.");
            return;
          }
        } else {
          if (username.length < 3) {
            setError("Username must be at least 3 characters.");
            return;
          }
          if (password.length < 4) {
            setError("Password must be at least 4 characters.");
            return;
          }
          const ok = await signup(username, password, displayName || username);
          if (!ok) {
            setError("Username is already taken. Try another one.");
            return;
          }
        }
        router.push("/");
      } finally {
        setIsSubmitting(false);
      }
    },
    [mode, username, password, displayName, login, signup, router],
  );

  return (
    <div className="relative flex min-h-dvh items-center justify-center overflow-hidden bg-background px-4">
      <WeatherBackground />

      <motion.div
        initial={{ opacity: 0, y: 30, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={springGentle}
        className="relative z-10 w-full max-w-sm"
      >
        <div className="rounded-3xl border border-border/60 bg-card/80 p-8 shadow-(--shadow-warm-lg) glass glass-border">
          {/* Logo */}
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={springBouncy}
            className="mx-auto mb-6 flex size-16 items-center justify-center rounded-2xl bg-primary/10"
          >
            <Heart className="size-8 text-primary" fill="currentColor" />
          </motion.div>

          <motion.h1
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.1 }}
            className="mb-1 text-center text-2xl font-bold font-heading text-foreground"
          >
            港伴<span className="text-primary">AI</span>
          </motion.h1>
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.15 }}
            className="mb-6 text-center text-sm text-muted-foreground"
          >
            Your warm AI companion for Hong Kong
          </motion.p>

          {/* Tab Toggle */}
          <div className="relative mb-6 flex rounded-xl bg-muted/50 p-1">
            {(["login", "signup"] as Mode[]).map((m) => (
              <button
                key={m}
                onClick={() => {
                  setMode(m);
                  setError(null);
                }}
                className="relative z-10 flex flex-1 items-center justify-center gap-1.5 rounded-lg py-2 text-sm font-medium transition-colors cursor-pointer"
                style={{ color: m === mode ? "var(--primary-foreground)" : "var(--muted-foreground)" }}
              >
                {m === "login" ? <LogIn className="size-3.5" /> : <UserPlus className="size-3.5" />}
                {m === "login" ? "Log In" : "Sign Up"}
                {m === mode && (
                  <motion.div
                    layoutId="auth-tab"
                    className="absolute inset-0 rounded-lg bg-primary"
                    style={{ zIndex: -1 }}
                    transition={spring}
                  />
                )}
              </button>
            ))}
          </div>

          <form onSubmit={(e) => void handleSubmit(e)} className="flex flex-col gap-3">
            <AnimatePresence mode="wait">
              {mode === "signup" && (
                <motion.div
                  key="display-name"
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={springGentle}
                >
                  <label className="mb-1 block text-xs font-medium text-muted-foreground">
                    Display Name
                  </label>
                  <div className="relative">
                    <Sparkles className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground/40" />
                    <Input
                      placeholder="How should we call you?"
                      value={displayName}
                      onChange={(e) => setDisplayName(e.target.value)}
                      className="pl-9"
                    />
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            <div>
              <label className="mb-1 block text-xs font-medium text-muted-foreground">
                Username
              </label>
              <Input
                placeholder="Enter your username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                autoComplete="username"
              />
            </div>

            <div>
              <label className="mb-1 block text-xs font-medium text-muted-foreground">
                Password
              </label>
              <div className="relative">
                <Input
                  type={showPassword ? "text" : "password"}
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  autoComplete={mode === "login" ? "current-password" : "new-password"}
                  className="pr-9"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((p) => !p)}
                  className="absolute right-2.5 top-1/2 -translate-y-1/2 text-muted-foreground/50 transition-colors hover:text-muted-foreground cursor-pointer"
                  tabIndex={-1}
                >
                  {showPassword ? <EyeOff className="size-4" /> : <Eye className="size-4" />}
                </button>
              </div>
            </div>

            <AnimatePresence>
              {error && (
                <motion.p
                  initial={{ opacity: 0, y: -4 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -4 }}
                  className="rounded-lg bg-destructive/10 px-3 py-2 text-xs text-destructive"
                >
                  {error}
                </motion.p>
              )}
            </AnimatePresence>

            <Button
              type="submit"
              disabled={isSubmitting || !username || !password}
              className="mt-2 w-full rounded-xl"
            >
              {isSubmitting ? (
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ repeat: Infinity, duration: 0.8, ease: "linear" }}
                  className="size-4 rounded-full border-2 border-primary-foreground border-t-transparent"
                />
              ) : mode === "login" ? (
                "Log In"
              ) : (
                "Create Account"
              )}
            </Button>
          </form>
        </div>
      </motion.div>
    </div>
  );
}
