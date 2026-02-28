import type { Role } from "@/features/chat/types";

export type RoleSlug = "companion" | "guide" | "study";

const SLUG_TO_ROLE: Record<RoleSlug, Role> = {
  companion: "companion",
  guide: "local_guide",
  study: "study_guide",
};

const ROLE_TO_SLUG: Record<Role, RoleSlug> = {
  companion: "companion",
  local_guide: "guide",
  study_guide: "study",
};

export function slugToRole(slug: string): Role | null {
  if (slug === "companion" || slug === "guide" || slug === "study") {
    return SLUG_TO_ROLE[slug];
  }
  if (slug === "local_guide" || slug === "study_guide") {
    return slug;
  }
  return null;
}

export function roleToSlug(role: Role): RoleSlug {
  return ROLE_TO_SLUG[role];
}
