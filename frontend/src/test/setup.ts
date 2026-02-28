import "@testing-library/jest-dom/vitest";
import { beforeEach, vi } from "vitest";

HTMLElement.prototype.scrollIntoView = () => {};

const mockRouter = {
  push: vi.fn(),
  replace: vi.fn(),
  prefetch: vi.fn(),
  back: vi.fn(),
  forward: vi.fn(),
  refresh: vi.fn(),
};

vi.mock("next/navigation", () => ({
  useRouter: () => mockRouter,
  redirect: vi.fn(),
  usePathname: () => "/",
  useSearchParams: () => new URLSearchParams(),
}));

beforeEach(() => {
  Object.values(mockRouter).forEach((fn) => fn.mockReset());
});
