"use client";

import {
  useCallback,
  useEffect,
  useLayoutEffect,
  useRef,
  useState,
  type KeyboardEvent,
} from "react";
import { motion, AnimatePresence, useReducedMotion } from "framer-motion";
import { Heart, MapPin, BookOpen, Send, ChevronDown, ArrowLeft } from "lucide-react";
import { useRouter } from "next/navigation";
import ReactMarkdown from "react-markdown";
import rehypeSanitize from "rehype-sanitize";
import remarkGfm from "remark-gfm";
import { Button } from "@/components/ui/button";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { ScrollArea } from "@/components/ui/scroll-area";
import { SafetyBanner } from "@/components/safety-banner";
import { WeatherIsland } from "@/components/weather-island";
import { parseAssistantMessage } from "@/features/chat/assistant-message-parser";
import { roleToSlug } from "@/features/chat/role-routing";
import { MapCanvas } from "@/features/recommendations/map-canvas";
import { RecommendationList } from "@/features/recommendations/recommendation-list";
import type { RecommendationResponse } from "@/features/recommendations/types";
import type { ChatResponse, Role } from "@/features/chat/types";
import { getChatHistory, postChatMessage } from "@/lib/api/chat";
import { postRecommendationHistory, postRecommendations } from "@/lib/api/recommendations";
import {
  spring,
  springGentle,
  springBouncy,
  fadeSlideUp,
  fadeScale,
  bubbleIn,
  staggerContainer,
} from "@/lib/motion-config";
import { cn } from "@/lib/utils";

type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  text: string;
  timestamp: number;
};

type LocalGuideTurnSummary = {
  assistantRequestId: string;
  timestamp: number;
  userQuery: string;
  assistantPreview: string;
};

const ROLE_OPTIONS: Role[] = ["companion", "local_guide", "study_guide"];

const ROLE_META: Record<
  Role,
  { label: string; icon: typeof Heart; description: string; empty: string }
> = {
  companion: {
    label: "Companion",
    icon: Heart,
    description: "Share how you feel and get supportive daily companionship.",
    empty: "Start by sharing how you are feeling today.",
  },
  local_guide: {
    label: "Local Guide",
    icon: MapPin,
    description: "Ask about places, routes, neighborhoods, and local options.",
    empty: "Tell me what area or activity you want to explore.",
  },
  study_guide: {
    label: "Study Guide",
    icon: BookOpen,
    description: "Plan study sessions, break down topics, and review concepts.",
    empty: "Share what you want to study and your timeline.",
  },
};

const HONG_KONG_FALLBACK = { latitude: 22.3193, longitude: 114.1694 };
const GOOGLE_MAPS_API_KEY = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY;
const MAX_TEXTAREA_HEIGHT = 120;

type Coordinates = { latitude: number; longitude: number };

function getBrowserCoordinates(timeoutMs = 2500): Promise<Coordinates | null> {
  return new Promise((resolve) => {
    if (!navigator.geolocation) {
      resolve(null);
      return;
    }
    let settled = false;
    const timer = window.setTimeout(() => {
      if (!settled) {
        settled = true;
        resolve(null);
      }
    }, timeoutMs);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        if (settled) return;
        settled = true;
        clearTimeout(timer);
        resolve({ latitude: pos.coords.latitude, longitude: pos.coords.longitude });
      },
      () => {
        if (settled) return;
        settled = true;
        clearTimeout(timer);
        resolve(null);
      },
      { enableHighAccuracy: false, timeout: timeoutMs, maximumAge: 5 * 60_000 },
    );
  });
}

interface ChatShellProps {
  initialRole?: Role;
  userId?: string;
}

function buildInitialThreadMap(userId: string): Record<Role, string> {
  return {
    companion: `${userId}-companion-thread`,
    local_guide: `${userId}-local_guide-thread`,
    study_guide: `${userId}-study_guide-thread`,
  };
}

function buildInitialMessageMap(): Record<Role, ChatMessage[]> {
  return { companion: [], local_guide: [], study_guide: [] };
}

function buildInitialBannerMap(): Record<Role, boolean> {
  return { companion: false, local_guide: false, study_guide: false };
}

function buildInitialSafetyMap(): Record<Role, ChatResponse["safety"] | null> {
  return { companion: null, local_guide: null, study_guide: null };
}

function buildInitialRoleFlagMap(initialValue: boolean): Record<Role, boolean> {
  return {
    companion: initialValue,
    local_guide: initialValue,
    study_guide: initialValue,
  };
}

function formatTime(ts: number): string {
  return new Date(ts).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function roleColor(role: Role): string {
  return `var(--role-${role.replace("_", "-")})`;
}

function compactText(input: string, maxLen: number): string {
  const normalized = input.replace(/\s+/g, " ").trim();
  if (normalized.length <= maxLen) return normalized;
  return `${normalized.slice(0, maxLen).trimEnd()}...`;
}

/* ─── TypingIndicator ─── */

function TypingIndicator() {
  const dotVariants = {
    initial: { opacity: 0.3, scale: 0.8 },
    animate: { opacity: 1, scale: 1 },
  };

  return (
    <motion.div
      variants={bubbleIn}
      initial="hidden"
      animate="visible"
      className="flex items-center gap-1.5 self-start rounded-(--radius-bubble) rounded-bl-md bg-card px-4 py-3 shadow-(--shadow-warm-sm)"
    >
      {[0, 1, 2].map((i) => (
        <motion.span
          key={i}
          className="size-2 rounded-full bg-muted-foreground"
          variants={dotVariants}
          initial="initial"
          animate="animate"
          transition={{
            repeat: Infinity,
            repeatType: "reverse",
            duration: 0.5,
            delay: i * 0.15,
            ease: "easeInOut",
          }}
        />
      ))}
    </motion.div>
  );
}

/* ─── ChatBubble ─── */

interface ChatBubbleProps {
  msg: ChatMessage;
  activeRole: Role;
  showRoleIcon: boolean;
}

function ChatBubble({ msg, activeRole, showRoleIcon }: ChatBubbleProps) {
  const isUser = msg.role === "user";
  const RoleIcon = ROLE_META[activeRole].icon;
  const [isThinkingOpen, setIsThinkingOpen] = useState(false);
  const parsedAssistantMessage = isUser ? null : parseAssistantMessage(msg.text);
  const hasThinking = Boolean(parsedAssistantMessage?.thinking);

  return (
    <motion.div
      variants={bubbleIn}
      whileHover={{ scale: 1.005, transition: { duration: 0.15 } }}
      className={cn("max-w-[85%]", isUser ? "self-end" : "self-start")}
    >
      <div className="flex items-end gap-2">
        {!isUser && showRoleIcon && (
          <motion.div
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={springBouncy}
            className="mb-1 flex size-7 shrink-0 items-center justify-center rounded-full"
            style={{
              backgroundColor: `color-mix(in srgb, ${roleColor(activeRole)} 15%, transparent)`,
            }}
          >
            <RoleIcon className="size-3.5" style={{ color: roleColor(activeRole) }} />
          </motion.div>
        )}
        {!isUser && !showRoleIcon && <div className="w-7 shrink-0" />}

        <div className="flex flex-col gap-0.5">
          <div
            className={cn(
              "px-4 py-2.5 text-[0.9375rem] leading-relaxed",
              isUser
                ? "rounded-(--radius-bubble) rounded-br-md bg-primary text-primary-foreground"
                : "rounded-(--radius-bubble) rounded-bl-md border-l-2 bg-card text-card-foreground shadow-(--shadow-warm-sm)",
            )}
            style={!isUser ? { borderLeftColor: roleColor(activeRole) } : undefined}
          >
            {isUser ? (
              <p className="whitespace-pre-wrap">{msg.text}</p>
            ) : (
              <div className="flex flex-col gap-2">
                <div className="chat-markdown">
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    rehypePlugins={[rehypeSanitize]}
                  >
                    {parsedAssistantMessage?.finalAnswer ?? msg.text}
                  </ReactMarkdown>
                </div>
                {hasThinking && (
                  <Collapsible open={isThinkingOpen} onOpenChange={setIsThinkingOpen}>
                    <CollapsibleTrigger asChild>
                      <button
                        type="button"
                        className="inline-flex items-center gap-1 rounded-md border border-border/70 bg-muted/50 px-2 py-1 text-[0.72rem] font-medium text-muted-foreground transition-colors hover:bg-muted"
                      >
                        <ChevronDown
                          className={cn(
                            "size-3 transition-transform duration-200",
                            isThinkingOpen && "rotate-180",
                          )}
                        />
                        Reasoning
                      </button>
                    </CollapsibleTrigger>
                    <CollapsibleContent className="mt-1 rounded-md border border-border/70 bg-muted/40 px-2.5 py-2 text-xs text-muted-foreground whitespace-pre-wrap">
                      {parsedAssistantMessage?.thinking}
                    </CollapsibleContent>
                  </Collapsible>
                )}
              </div>
            )}
          </div>
          <span
            className={cn(
              "text-[0.65rem] text-muted-foreground/50 select-none",
              isUser ? "text-right" : "text-left",
            )}
          >
            {formatTime(msg.timestamp)}
          </span>
        </div>
      </div>
    </motion.div>
  );
}

/* ─── ScrollToBottomFAB ─── */

function ScrollToBottomFAB({ onClick }: { onClick: () => void }) {
  return (
    <motion.button
      initial={{ opacity: 0, y: 8, scale: 0.9 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: 8, scale: 0.9 }}
      transition={spring}
      onClick={onClick}
      className="absolute bottom-2 left-1/2 z-10 flex -translate-x-1/2 items-center gap-1 rounded-full bg-card/90 px-3 py-1.5 text-xs font-medium text-muted-foreground shadow-(--shadow-warm-md) glass glass-border cursor-pointer hover:bg-card transition-colors"
      aria-label="Scroll to latest messages"
    >
      <ChevronDown className="size-3.5" />
      New messages
    </motion.button>
  );
}

/* ─── AutoGrowTextarea ─── */

interface AutoGrowTextareaProps {
  value: string;
  onChange: (value: string) => void;
  onKeyDown: (e: KeyboardEvent<HTMLTextAreaElement>) => void;
  placeholder: string;
  disabled: boolean;
  textareaRef: React.RefObject<HTMLTextAreaElement | null>;
}

function AutoGrowTextarea({
  value,
  onChange,
  onKeyDown,
  placeholder,
  disabled,
  textareaRef,
}: AutoGrowTextareaProps) {
  useLayoutEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "0";
    el.style.height = `${Math.min(el.scrollHeight, MAX_TEXTAREA_HEIGHT)}px`;
  }, [value, textareaRef]);

  return (
    <textarea
      ref={textareaRef}
      aria-label="Message input"
      className={cn(
        "flex-1 resize-none rounded-xl border border-input bg-card px-3 py-2 text-base text-foreground placeholder:text-muted-foreground shadow-(--shadow-warm-sm) outline-none md:text-sm",
        "transition-[color,box-shadow,height] duration-150",
        "focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px]",
        "disabled:pointer-events-none disabled:opacity-50",
      )}
      style={{ minHeight: 38, maxHeight: MAX_TEXTAREA_HEIGHT }}
      rows={1}
      placeholder={placeholder}
      value={value}
      disabled={disabled}
      onChange={(e) => onChange(e.target.value)}
      onKeyDown={onKeyDown}
    />
  );
}

/* ═══════════════════════════════════════════════════════════
   ChatShell — main component
   ═══════════════════════════════════════════════════════════ */

export function ChatShell({ initialRole = "companion", userId = "demo-user" }: ChatShellProps) {
  const router = useRouter();
  const prefersReducedMotion = useReducedMotion();
  const [activeRole, setActiveRole] = useState<Role>(initialRole);
  const threadIdRef = useRef(buildInitialThreadMap(userId));
  const historyLoadedRef = useRef(buildInitialRoleFlagMap(false));
  const historyLoadingRef = useRef(buildInitialRoleFlagMap(false));
  const [messagesByRole, setMessagesByRole] =
    useState<Record<Role, ChatMessage[]>>(buildInitialMessageMap());
  const [input, setInput] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showCrisisBannerByRole, setShowCrisisBannerByRole] =
    useState<Record<Role, boolean>>(buildInitialBannerMap());
  const [safetyByRole, setSafetyByRole] =
    useState<Record<Role, ChatResponse["safety"] | null>>(buildInitialSafetyMap());
  const [isHistoryLoadingByRole, setIsHistoryLoadingByRole] =
    useState<Record<Role, boolean>>(buildInitialRoleFlagMap(false));
  const [coordinates, setCoordinates] = useState<Coordinates | null>(null);
  const [recommendationsByAssistantRequestId, setRecommendationsByAssistantRequestId] = useState<
    Record<string, RecommendationResponse>
  >({});
  const [recommendationErrorByAssistantRequestId, setRecommendationErrorByAssistantRequestId] =
    useState<Record<string, string | null>>({});
  const [recommendationLoadingByAssistantRequestId, setRecommendationLoadingByAssistantRequestId] =
    useState<Record<string, boolean>>({});
  const [selectedRecommendationRequestId, setSelectedRecommendationRequestId] = useState<
    string | null
  >(null);
  const [showScrollFAB, setShowScrollFAB] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const messagesByRoleRef = useRef(messagesByRole);

  const activeMessages = messagesByRole[activeRole];
  const localGuideTurnSummaries: LocalGuideTurnSummary[] = (() => {
    const summaries: LocalGuideTurnSummary[] = [];
    let lastUserMessage = "";
    for (const message of messagesByRole.local_guide) {
      if (message.role === "user") {
        lastUserMessage = message.text;
        continue;
      }
      const assistantPreview = parseAssistantMessage(message.text).finalAnswer;
      summaries.push({
        assistantRequestId: message.id,
        timestamp: message.timestamp,
        userQuery: lastUserMessage,
        assistantPreview,
      });
    }
    return summaries;
  })();
  const localGuideAssistantRequestIds = localGuideTurnSummaries.map((turn) => turn.assistantRequestId);
  const resolvedSelectedRecommendationRequestId = (() => {
    if (activeRole !== "local_guide") return null;
    if (selectedRecommendationRequestId) return selectedRecommendationRequestId;
    return localGuideAssistantRequestIds.at(-1) ?? null;
  })();
  const selectedTurnSummary = resolvedSelectedRecommendationRequestId
    ? localGuideTurnSummaries.find(
        (turn) => turn.assistantRequestId === resolvedSelectedRecommendationRequestId,
      ) ?? null
    : null;
  const selectedRecommendationResponse = resolvedSelectedRecommendationRequestId
    ? recommendationsByAssistantRequestId[resolvedSelectedRecommendationRequestId] ?? null
    : null;
  const selectedRecommendationError = resolvedSelectedRecommendationRequestId
    ? recommendationErrorByAssistantRequestId[resolvedSelectedRecommendationRequestId] ?? null
    : null;
  const isSelectedRecommendationLoading = resolvedSelectedRecommendationRequestId
    ? Boolean(recommendationLoadingByAssistantRequestId[resolvedSelectedRecommendationRequestId])
    : false;
  const activeRecommendations = selectedRecommendationResponse?.recommendations ?? [];
  const recommendationCenter =
    activeRecommendations[0]?.location ?? coordinates ?? HONG_KONG_FALLBACK;
  const meta = ROLE_META[activeRole];

  useEffect(() => {
    messagesByRoleRef.current = messagesByRole;
  }, [messagesByRole]);

  useEffect(() => {
    let active = true;
    async function resolve() {
      const coords = await getBrowserCoordinates();
      if (active) setCoordinates(coords ?? HONG_KONG_FALLBACK);
    }
    void resolve();
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    setActiveRole(initialRole);
  }, [initialRole]);

  const hydrateRoleHistory = useCallback(
    async (roleToLoad: Role) => {
      if (historyLoadedRef.current[roleToLoad] || historyLoadingRef.current[roleToLoad]) return;

      historyLoadingRef.current[roleToLoad] = true;
      setIsHistoryLoadingByRole((prev) => ({ ...prev, [roleToLoad]: true }));

      try {
        const history = await getChatHistory({
          user_id: userId,
          role: roleToLoad,
          thread_id: threadIdRef.current[roleToLoad],
          limit: 50,
        });

        threadIdRef.current[roleToLoad] = history.thread_id;
        const hydratedMessages: ChatMessage[] = [];
        history.turns.forEach((turn) => {
          const baseTs = Date.parse(turn.created_at);
          const timestamp = Number.isNaN(baseTs) ? Date.now() : baseTs;
          hydratedMessages.push({
            id: `${turn.request_id}-user`,
            role: "user",
            text: turn.user_message,
            timestamp,
          });
          hydratedMessages.push({
            id: turn.request_id,
            role: "assistant",
            text: turn.assistant_reply,
            timestamp: timestamp + 1,
          });
        });

        const hadMessagesAtApplyTime = messagesByRoleRef.current[roleToLoad].length > 0;
        setMessagesByRole((prev) => {
          const existingMessages = prev[roleToLoad];
          if (existingMessages.length === 0) {
            return { ...prev, [roleToLoad]: hydratedMessages };
          }
          const seenIds = new Set<string>();
          const mergedMessages: ChatMessage[] = [];
          [...hydratedMessages, ...existingMessages].forEach((message) => {
            if (seenIds.has(message.id)) return;
            seenIds.add(message.id);
            mergedMessages.push(message);
          });
          return { ...prev, [roleToLoad]: mergedMessages };
        });
        if (!hadMessagesAtApplyTime) {
          const latestTurn = history.turns.at(-1) ?? null;
          setSafetyByRole((prev) => ({ ...prev, [roleToLoad]: latestTurn?.safety ?? null }));
          setShowCrisisBannerByRole((prev) => ({
            ...prev,
            [roleToLoad]: history.turns.some((turn) => turn.safety.show_crisis_banner),
          }));
        }

        if (roleToLoad === "local_guide") {
          const assistantRequestIds = history.turns.map((turn) => turn.request_id);
          if (assistantRequestIds.length > 0) {
            try {
              const recommendationHistory = await postRecommendationHistory({
                user_id: userId,
                role: "local_guide",
                request_ids: assistantRequestIds,
              });
              const nextRecommendationMap: Record<string, RecommendationResponse> = {};
              recommendationHistory.results.forEach((result) => {
                nextRecommendationMap[result.request_id] = result;
              });
              setRecommendationsByAssistantRequestId((prev) => ({
                ...prev,
                ...nextRecommendationMap,
              }));
            } catch (fetchError) {
              setError(
                fetchError instanceof Error
                  ? fetchError.message
                  : "Unable to restore local recommendations.",
              );
            }
          }
          setSelectedRecommendationRequestId(assistantRequestIds.at(-1) ?? null);
        }

        historyLoadedRef.current[roleToLoad] = true;
      } catch (historyError) {
        setError(
          historyError instanceof Error
            ? historyError.message
            : `Unable to restore ${ROLE_META[roleToLoad].label} history.`,
        );
      } finally {
        historyLoadingRef.current[roleToLoad] = false;
        setIsHistoryLoadingByRole((prev) => ({ ...prev, [roleToLoad]: false }));
      }
    },
    [userId],
  );

  useEffect(() => {
    void hydrateRoleHistory(activeRole);
  }, [activeRole, hydrateRoleHistory]);

  useEffect(() => {
    if (activeRole !== "local_guide") return;
    if (localGuideAssistantRequestIds.length === 0) {
      if (selectedRecommendationRequestId !== null) {
        setSelectedRecommendationRequestId(null);
      }
      return;
    }
    const hasSelected =
      selectedRecommendationRequestId != null &&
      localGuideAssistantRequestIds.includes(selectedRecommendationRequestId);
    if (!hasSelected) {
      setSelectedRecommendationRequestId(localGuideAssistantRequestIds.at(-1) ?? null);
    }
  }, [activeRole, localGuideAssistantRequestIds, selectedRecommendationRequestId]);

  const ensureRecommendationsForTurn = useCallback(
    async (assistantRequestId: string) => {
      if (
        recommendationsByAssistantRequestId[assistantRequestId] ||
        recommendationLoadingByAssistantRequestId[assistantRequestId]
      ) {
        return;
      }
      const turnSummary = localGuideTurnSummaries.find(
        (turn) => turn.assistantRequestId === assistantRequestId,
      );
      const query = turnSummary?.userQuery.trim();
      if (!query) {
        setRecommendationErrorByAssistantRequestId((prev) => ({
          ...prev,
          [assistantRequestId]: "No linked user query found for this turn.",
        }));
        return;
      }

      const loc = coordinates ?? HONG_KONG_FALLBACK;
      setRecommendationErrorByAssistantRequestId((prev) => ({
        ...prev,
        [assistantRequestId]: null,
      }));
      setRecommendationLoadingByAssistantRequestId((prev) => ({
        ...prev,
        [assistantRequestId]: true,
      }));

      try {
        const recommendationResponse = await postRecommendations({
          user_id: userId,
          role: "local_guide",
          query,
          latitude: loc.latitude,
          longitude: loc.longitude,
          chat_request_id: assistantRequestId,
          max_results: 5,
          travel_mode: "walking",
        });
        setRecommendationsByAssistantRequestId((prev) => ({
          ...prev,
          [assistantRequestId]: recommendationResponse,
        }));
      } catch (recommendationError) {
        setRecommendationErrorByAssistantRequestId((prev) => ({
          ...prev,
          [assistantRequestId]:
            recommendationError instanceof Error
              ? recommendationError.message
              : "Unable to load recommendations for this turn.",
        }));
      } finally {
        setRecommendationLoadingByAssistantRequestId((prev) => ({
          ...prev,
          [assistantRequestId]: false,
        }));
      }
    },
    [
      coordinates,
      localGuideTurnSummaries,
      recommendationLoadingByAssistantRequestId,
      recommendationsByAssistantRequestId,
      userId,
    ],
  );

  const handleSelectRecommendationTurn = useCallback(
    (assistantRequestId: string) => {
      setSelectedRecommendationRequestId(assistantRequestId);
      void ensureRecommendationsForTurn(assistantRequestId);
    },
    [ensureRecommendationsForTurn],
  );

  useEffect(() => {
    if (activeRole !== "local_guide" || !resolvedSelectedRecommendationRequestId) return;
    const alreadyResolved =
      recommendationsByAssistantRequestId[resolvedSelectedRecommendationRequestId] != null ||
      recommendationLoadingByAssistantRequestId[resolvedSelectedRecommendationRequestId] ||
      recommendationErrorByAssistantRequestId[resolvedSelectedRecommendationRequestId];
    if (!alreadyResolved) {
      void ensureRecommendationsForTurn(resolvedSelectedRecommendationRequestId);
    }
  }, [
    activeRole,
    ensureRecommendationsForTurn,
    recommendationErrorByAssistantRequestId,
    recommendationLoadingByAssistantRequestId,
    recommendationsByAssistantRequestId,
    resolvedSelectedRecommendationRequestId,
  ]);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: prefersReducedMotion ? "auto" : "smooth" });
    setShowScrollFAB(false);
  }, [prefersReducedMotion]);

  useEffect(() => {
    scrollToBottom();
  }, [activeMessages.length, isSubmitting, scrollToBottom]);

  useEffect(() => {
    textareaRef.current?.focus();
  }, [activeRole]);

  useEffect(() => {
    const el = scrollAreaRef.current;
    if (!el) return;
    function handleScroll() {
      if (!el) return;
      const distFromBottom = el.scrollHeight - el.scrollTop - el.clientHeight;
      setShowScrollFAB(distFromBottom > 120);
    }
    el.addEventListener("scroll", handleScroll, { passive: true });
    return () => el.removeEventListener("scroll", handleScroll);
  }, []);

  const handleSend = async () => {
    const trimmed = input.trim();
    if (!trimmed || isSubmitting) return;

    const roleAtSend = activeRole;
    const threadId = threadIdRef.current[roleAtSend];
    setError(null);
    setInput("");
    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      text: trimmed,
      timestamp: Date.now(),
    };
    setMessagesByRole((prev) => ({ ...prev, [roleAtSend]: [...prev[roleAtSend], userMsg] }));
    setIsSubmitting(true);

    try {
      const res = await postChatMessage({
        user_id: userId,
        role: roleAtSend,
        thread_id: threadId,
        message: trimmed,
      });
      const assistantMsg: ChatMessage = {
        id: res.request_id,
        role: "assistant",
        text: res.reply,
        timestamp: Date.now(),
      };
      threadIdRef.current[roleAtSend] = res.thread_id;
      setMessagesByRole((prev) => ({ ...prev, [roleAtSend]: [...prev[roleAtSend], assistantMsg] }));
      setSafetyByRole((prev) => ({ ...prev, [roleAtSend]: res.safety }));
      if (res.safety.show_crisis_banner) {
        setShowCrisisBannerByRole((prev) => ({ ...prev, [roleAtSend]: true }));
      }

      if (roleAtSend === "local_guide") {
        const assistantRequestId = res.request_id;
        const loc = coordinates ?? HONG_KONG_FALLBACK;
        setSelectedRecommendationRequestId(assistantRequestId);
        setRecommendationErrorByAssistantRequestId((prev) => ({
          ...prev,
          [assistantRequestId]: null,
        }));
        setRecommendationLoadingByAssistantRequestId((prev) => ({
          ...prev,
          [assistantRequestId]: true,
        }));
        try {
          const recommendationResponse = await postRecommendations({
            user_id: userId,
            role: roleAtSend,
            query: trimmed,
            latitude: loc.latitude,
            longitude: loc.longitude,
            chat_request_id: assistantRequestId,
            max_results: 5,
            travel_mode: "walking",
          });
          setRecommendationsByAssistantRequestId((prev) => ({
            ...prev,
            [assistantRequestId]: recommendationResponse,
          }));
        } catch (recommendationError) {
          setRecommendationErrorByAssistantRequestId((prev) => ({
            ...prev,
            [assistantRequestId]:
              recommendationError instanceof Error
                ? recommendationError.message
                : "Unable to load recommendations.",
          }));
        } finally {
          setRecommendationLoadingByAssistantRequestId((prev) => ({
            ...prev,
            [assistantRequestId]: false,
          }));
        }
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unable to send message.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      void handleSend();
    }
  };

  return (
    <div className="flex min-h-dvh flex-col">
      {/* ─── Header ─── */}
      <motion.header
        initial={{ opacity: 0, y: -12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={springGentle}
        className="relative flex items-center justify-between px-4 py-3 md:px-6 glass"
      >
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="icon-sm"
            onClick={() => router.push("/")}
            className="rounded-lg text-muted-foreground"
            aria-label="Back to home"
          >
            <ArrowLeft className="size-4" />
          </Button>
          <span className="text-xl font-bold font-heading text-foreground tracking-tight">
            港伴<span className="text-primary">AI</span>
          </span>
        </div>
        <WeatherIsland />
        <div
          className="absolute inset-x-0 bottom-0 h-px"
          style={{
            background: `linear-gradient(90deg, transparent, ${roleColor(activeRole)}, transparent)`,
            opacity: 0.3,
          }}
        />
      </motion.header>

      {/* ─── Role Selector ─── */}
      <nav className="relative flex justify-center gap-2 px-4 pb-2 pt-1" aria-label="Role spaces">
        {ROLE_OPTIONS.map((role) => {
          const { label, icon: Icon } = ROLE_META[role];
          const isActive = role === activeRole;
          const color = roleColor(role);
          return (
            <motion.button
              key={role}
              onClick={() => {
                setActiveRole(role);
                router.replace(`/chat/${roleToSlug(role)}`);
              }}
              whileTap={{ scale: 0.95 }}
              className={cn(
                "relative flex items-center gap-1.5 rounded-full px-4 py-2 text-sm font-semibold cursor-pointer",
                "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
                "transition-colors duration-200",
                isActive
                  ? "text-white"
                  : "bg-card text-muted-foreground hover:bg-muted hover:text-foreground",
              )}
              style={isActive ? { backgroundColor: color } : undefined}
              aria-current={isActive ? "page" : undefined}
            >
              {isActive && (
                <motion.span
                  layoutId="role-pill"
                  className="absolute inset-0 rounded-full shadow-(--shadow-warm-md)"
                  style={{ backgroundColor: color }}
                  transition={spring}
                />
              )}
              <span className="relative z-10 flex items-center gap-1.5">
                <Icon className="size-4" />
                {label}
              </span>
            </motion.button>
          );
        })}
      </nav>

      {/* ─── Role Description ─── */}
      <div className="px-4 pb-2 text-center md:px-6">
        <AnimatePresence mode="wait">
          <motion.p
            key={activeRole}
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -4 }}
            transition={{ duration: 0.2 }}
            className="text-sm text-muted-foreground"
          >
            {meta.description}
          </motion.p>
        </AnimatePresence>
      </div>

      {/* ─── Safety Banner ─── */}
      {showCrisisBannerByRole[activeRole] && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: "auto" }}
          transition={springGentle}
          className="px-4 pb-2 md:px-6 overflow-hidden"
        >
          <SafetyBanner
            onDismiss={() =>
              setShowCrisisBannerByRole((prev) => ({ ...prev, [activeRole]: false }))
            }
          />
        </motion.div>
      )}

      {/* ─── Chat Messages ─── */}
      <div className="relative mx-auto flex w-full max-w-2xl flex-1 flex-col px-4 md:px-6">
        <ScrollArea className="flex-1 py-4" ref={scrollAreaRef}>
          <AnimatePresence mode="popLayout">
            <motion.div
              key={activeRole}
              variants={fadeScale}
              initial="hidden"
              animate="visible"
              exit="exit"
              transition={{ duration: 0.15 }}
              className="flex flex-col gap-3"
              role="log"
              aria-live="polite"
              aria-label={`${meta.label} conversation`}
            >
              {activeMessages.length === 0 && (
                <div className="flex flex-1 flex-col items-center justify-center py-16 text-center">
                  <motion.div
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={springBouncy}
                  >
                    <meta.icon className="mb-4 size-12 text-muted-foreground/40 animate-float" />
                  </motion.div>
                  <motion.p
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1, ...springGentle }}
                    className="text-base font-medium text-muted-foreground"
                  >
                    {isHistoryLoadingByRole[activeRole] ? "Loading conversation..." : meta.empty}
                  </motion.p>
                </div>
              )}

              {activeMessages.length > 0 && (
                <motion.div
                  variants={staggerContainer}
                  initial="hidden"
                  animate="visible"
                  className="flex flex-col gap-3"
                >
                  {activeMessages.map((msg, idx) => {
                    const prevMsg = activeMessages[idx - 1];
                    const showRoleIcon =
                      msg.role === "assistant" && (idx === 0 || prevMsg?.role !== "assistant");
                    return (
                      <ChatBubble
                        key={msg.id}
                        msg={msg}
                        activeRole={activeRole}
                        showRoleIcon={showRoleIcon}
                      />
                    );
                  })}
                </motion.div>
              )}

              <AnimatePresence>{isSubmitting && <TypingIndicator />}</AnimatePresence>
              <div ref={messagesEndRef} />
            </motion.div>
          </AnimatePresence>
        </ScrollArea>

        <AnimatePresence>
          {showScrollFAB && <ScrollToBottomFAB onClick={scrollToBottom} />}
        </AnimatePresence>

        <AnimatePresence>
          {error && (
            <motion.div
              variants={fadeSlideUp}
              initial="hidden"
              animate="visible"
              exit="exit"
              transition={spring}
              className="mb-2 rounded-xl border border-destructive/30 bg-destructive/10 px-4 py-2.5 text-sm text-destructive"
            >
              {error}
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* ─── Local Guide Recommendations ─── */}
      <AnimatePresence>
        {activeRole === "local_guide" && (
          <motion.div
            key="rec-panel"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={springGentle}
            className="mx-auto w-full max-w-2xl overflow-hidden px-4 pb-2 md:px-6"
          >
            {localGuideTurnSummaries.length > 0 && (
              <div className="mb-2">
                <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                  Linked Recommendation Turns
                </p>
                <div className="flex gap-2 overflow-x-auto pb-1">
                  {localGuideTurnSummaries.map((turn) => {
                    const isSelected =
                      turn.assistantRequestId === resolvedSelectedRecommendationRequestId;
                    const linkedResponse = recommendationsByAssistantRequestId[turn.assistantRequestId];
                    const isLoading = Boolean(
                      recommendationLoadingByAssistantRequestId[turn.assistantRequestId],
                    );
                    const turnError = recommendationErrorByAssistantRequestId[turn.assistantRequestId];
                    const statusLabel = isLoading
                      ? "Loading"
                      : linkedResponse
                        ? linkedResponse.context.degraded
                          ? "Fallback"
                          : "Live"
                        : turnError
                          ? "Retry"
                          : "Tap to load";
                    return (
                      <button
                        key={turn.assistantRequestId}
                        type="button"
                        onClick={() => handleSelectRecommendationTurn(turn.assistantRequestId)}
                        className={cn(
                          "min-w-56 rounded-xl border px-3 py-2.5 text-left transition-colors",
                          isSelected
                            ? "border-primary bg-primary/10 text-foreground"
                            : "border-border/60 bg-card text-muted-foreground hover:bg-muted",
                        )}
                      >
                        <div className="mb-1 flex items-center justify-between gap-2">
                          <span className="text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">
                            {formatTime(turn.timestamp)}
                          </span>
                          <span
                            className={cn(
                              "rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide",
                              statusLabel === "Live"
                                ? "bg-emerald-100 text-emerald-700"
                                : statusLabel === "Fallback"
                                  ? "bg-amber-100 text-amber-700"
                                  : "bg-muted text-muted-foreground",
                            )}
                          >
                            {statusLabel}
                          </span>
                        </div>
                        <p className="line-clamp-2 text-sm font-semibold text-foreground">
                          {compactText(turn.userQuery || "Local Guide request", 72)}
                        </p>
                        <p className="mt-1 line-clamp-2 text-xs text-muted-foreground">
                          {compactText(turn.assistantPreview || "Local Guide response", 96)}
                        </p>
                      </button>
                    );
                  })}
                </div>
              </div>
            )}

            {selectedRecommendationError && (
              <div className="mb-2 rounded-xl border border-accent/30 bg-accent/10 px-4 py-2.5 text-sm text-accent-foreground">
                {selectedRecommendationError}
              </div>
            )}
            {isSelectedRecommendationLoading && (
              <p className="mb-2 text-sm text-muted-foreground animate-pulse-gentle">
                Fetching local recommendations...
              </p>
            )}
            {!isSelectedRecommendationLoading &&
              !selectedRecommendationError &&
              activeRecommendations.length === 0 &&
              localGuideTurnSummaries.length > 0 && (
                <p className="mb-2 text-sm text-muted-foreground">
                  No place recommendations were returned for this turn.
                </p>
              )}
            {activeMessages.length > 0 && localGuideTurnSummaries.length === 0 && (
              <p className="mb-2 text-sm text-muted-foreground">
                Waiting for Local Guide response before loading map suggestions.
              </p>
            )}
            {activeRecommendations.length > 0 && (
              <div className="flex flex-col gap-3 pb-2">
                {selectedRecommendationResponse && (
                  <div className="flex flex-col gap-1">
                    <p className="text-xs text-muted-foreground">
                      Weather: {selectedRecommendationResponse.context.weather_condition}
                      {selectedRecommendationResponse.context.temperature_c != null
                        ? ` · ${selectedRecommendationResponse.context.temperature_c.toFixed(1)}°C`
                        : ""}
                    </p>
                    {selectedRecommendationResponse.context.degraded && (
                      <p className="text-xs text-amber-700">
                        Live place data is limited for this turn. Showing best available fallback
                        results.
                      </p>
                    )}
                    {selectedTurnSummary?.userQuery && (
                      <p className="text-xs text-muted-foreground">
                        Based on: <span className="font-medium">{selectedTurnSummary.userQuery}</span>
                      </p>
                    )}
                  </div>
                )}
                <MapCanvas
                  apiKey={GOOGLE_MAPS_API_KEY}
                  center={recommendationCenter}
                  recommendations={activeRecommendations}
                />
                <RecommendationList recommendations={activeRecommendations} />
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* ─── Input Bar ─── */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15, ...springGentle }}
        className="sticky bottom-0 border-t border-border/60 bg-background/80 glass glass-border"
      >
        <div className="mx-auto flex max-w-2xl items-end gap-2 px-4 py-3 md:px-6">
          <AutoGrowTextarea
            textareaRef={textareaRef}
            placeholder={meta.empty}
            value={input}
            disabled={isSubmitting}
            onChange={setInput}
            onKeyDown={handleKeyDown}
          />
          <motion.div whileTap={{ scale: 0.9 }} transition={springBouncy}>
            <Button
              size="icon"
              className="rounded-xl shadow-(--shadow-warm-sm) transition-all duration-200 hover:shadow-(--shadow-warm-md)"
              onClick={() => void handleSend()}
              disabled={isSubmitting || input.trim().length === 0}
              style={{ backgroundColor: roleColor(activeRole) }}
            >
              <Send className="size-4 text-white" />
              <span className="sr-only">Send</span>
            </Button>
          </motion.div>
        </div>
      </motion.div>
    </div>
  );
}
